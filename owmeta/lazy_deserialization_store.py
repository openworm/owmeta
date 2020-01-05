import logging
from os import makedirs, listdir, unlink, rename, rmdir
from os.path import join as p, exists, isdir, isfile
import shutil
import pickle
import re
from itertools import chain

from rdflib.store import Store
from rdflib.plugins.memory import IOMemory
from rdflib.term import URIRef

try:
    from urllib.parse import quote as urlquote, unquote as urlunquote
except ImportError:
    from urllib import quote as urlquote, unquote as urlunquote

L = logging.getLogger(__name__)

STORE_PICKLE_FNAME_REGEX = re.compile(r'(?P<index>\d+)\.(?P<type>[ra])\.pickle')
''' Regex for the base name of a pickled store '''


class LazyDeserializationStore(Store):
    '''
    Uses the `IOMemory` store as an in-memory cache and writes new triples to a pickling of
    the store
    '''

    context_aware = True

    def __init__(self, base_directory=None):
        '''
        Paramaters
        ----------
        base_directory : str
            Base directory where pickles are stored
        '''
        super(LazyDeserializationStore, self).__init__(base_directory)

    def open(self, base_directory, create=True):
        self.__active_store = IOMemory()
        self.__loaded_contexts = dict()
        self.__tentative_stores = dict()
        self.__removal_stores = dict()
        self.__base_directory = base_directory
        if not isdir(self.__base_directory):
            if create:
                makedirs(self.__base_directory)
            else:
                raise Exception('Base directory does not exist and `create` is not True')

    def close(self):
        self.__base_directory = None

    def add(self, triple, context=None, quoted=False):
        ctx = getattr(context, 'identifier', context)
        ctx_store = self.__tentative_stores.get(ctx)
        if ctx_store is None:
            ctx_store = self.__tentative_stores.setdefault(ctx, IOMemory())
        ctx_store.add(triple, ctx, quoted)

    def triples(self, triplepat, context=None):
        ctx = getattr(context, 'identifier', context)

        if ctx not in self.__loaded_contexts:
            self._merge(ctx, self.__active_store)
            self.__loaded_contexts[ctx] = True

        if ctx is None:
            # This is loading in every context available, which can be an arbitrary size
            # and we don't want to keep that in memory, so we just load and query a
            # context at a time.
            for ctxdirname in listdir(self.__base_directory):
                this_ctx = urlunquote(ctxdirname)
                has_loaded = self.__loaded_contexts.get(this_ctx)
                if has_loaded:
                    # We've already loaded the context, so any triples will be in the
                    # __active_store or in a tentative store.
                    continue
                store = IOMemory()
                if not self._merge(this_ctx, store, triplepat):
                    continue
                for m in store.triples(triplepat):
                    # We only make tentative stores for contexts we've previously loaded
                    # (possibly on-demand), so we don't have to check for tentative
                    # removals here.
                    yield m

        for trip, ctxs in self.__active_store.triples(triplepat, context=ctx):
            removals = self.__removal_stores.get(ctx)
            if removals:
                removed = next(removals.triples(trip, context=ctx), None)
            else:
                removed = False
            if not removed:
                yield trip, ctxs

        tent = self.__tentative_stores.get(ctx)
        if tent:
            tent_triples = tent.triples(triplepat, context=context)
            for trip, ctxs in tent_triples:
                yield trip, ctxs

    def remove(self, triplepat, context=None):
        ctx = getattr(context, 'identifier', context)
        if ctx not in self.__loaded_contexts:
            self._merge(ctx, self.__active_store)
            self.__loaded_contexts[ctx] = True
        active_store_matches = self.__active_store.triples(triplepat, context=ctx)
        has_triples = next(active_store_matches, None)
        if has_triples:
            ctx_store = self.__removal_stores.get(ctx)
            if ctx_store is None:
                ctx_store = self.__removal_stores.setdefault(ctx, IOMemory())
            ctx_store.add(has_triples[0], context=ctx)
            for trip, _ in active_store_matches:
                ctx_store.add(trip, context=ctx)
        tent = self.__tentative_stores.get(ctx)
        if tent:
            tent.remove(triplepat, context=ctx)

    def collapse(self, context):
        '''
        Collapse the revisions for the given context

        Not a standard `rdflib.store.Store` method.
        '''
        ctx = getattr(context, 'identifier', context)
        store = IOMemory()
        self._merge(ctx, store)
        has_triples = next(store.triples((None, None, None), context=ctx), None)
        ctxdir = self._format_context_directory_name(ctx)
        if has_triples:
            tempdir = p(ctxdir, 'temp')
            makedirs(tempdir, exist_ok=True)
            max_rev = self._max_rev(ctxdir)
            collapsed_basename = '%d.a.pickle' % max_rev
            collapsed_fname = p(tempdir, collapsed_basename)
            with open(collapsed_fname, 'wb') as f:
                pickle.dump(store, f)
        pickles = (x for x in (STORE_PICKLE_FNAME_REGEX.match(p) for p in listdir(ctxdir)) if x)

        # Note: even if there are no triples, we still need to unlink the revisions
        # because in that case we can just drop them
        try:
            for pickle_match_data in pickles:
                unlink(p(ctxdir, pickle_match_data.group(0)))
        except BaseException:
            L.error('Failed to complete collapse of revisions for %s' +
                    (has_triples and ', but the collapsed store is available at %s' % collapsed_fname or ''), context)
            raise
        if has_triples:
            rename(collapsed_fname, p(ctxdir, collapsed_basename))

    def commit(self):
        try:
            self.tpc_prepare()
        except BaseException:
            self.tpc_abort()
            raise
        else:
            self.tpc_commit()

    def tpc_prepare(self):
        self._dex(self.__tentative_stores, 'a',
                lambda triple, context: self.__active_store.add(triple[0],
                    context=context))
        self.__tentative_stores.clear()
        self._dex(self.__removal_stores, 'r',
                lambda triple, context: self.__active_store.remove(triple[0],
                    context=context))
        self.__removal_stores.clear()

    def tpc_commit(self):
        prepdir = p(self.__base_directory, 'prep')
        if not isdir(prepdir):
            return
        for ctx_fname in listdir(prepdir):
            this_ctx = urlunquote(ctx_fname)
            ctx_prepdir = p(prepdir, ctx_fname)
            for fname in listdir(ctx_prepdir):
                md = STORE_PICKLE_FNAME_REGEX.match(fname)
                if not md:
                    continue
                revision_fname = md.group(0)
                ctxdir = self._format_context_directory_name(this_ctx)
                rename(p(prepdir, ctx_prepdir, revision_fname),
                       p(ctxdir, revision_fname))
                rmdir(ctx_prepdir)
        rmdir(prepdir)

    def tpc_abort(self):
        self.__tentative_stores.clear()
        self.__removal_stores.clear()
        self.__active_store = IOMemory()
        prepdir = p(self.__base_directory, 'prep')

        if isdir(prepdir):
            shutil.rmtree(prepdir)

    def _dex(self, stores, revision_type, callback):
        for ctx, store in stores.items():
            store_triples = store.triples((None, None, None), context=ctx)
            has_triples = next(store_triples, None)
            if not has_triples:
                continue
            ctxdir = self._format_context_directory_name(ctx)
            makedirs(ctxdir, exist_ok=True)
            prepdir = self._format_context_prep_directory_name(ctx)
            makedirs(prepdir)
            max_rev = self._max_rev(ctxdir)
            revision_fname = p(prepdir, '%d.%s.pickle' % (max_rev + 1, revision_type))
            if isfile(revision_fname):
                # We don't recerate a prepared file...asume it's already fully prepped
                continue

            with open(revision_fname, 'wb') as f:
                pickle.dump(store, f)

            for triple in chain((has_triples,), store_triples):
                callback(triple, ctx)

    def _format_context_prep_directory_name(self, ctx):
        return p(self.__base_directory, 'prep', urlquote(ctx or '___', safe=''))

    def _format_context_directory_name(self, ctx):
        return p(self.__base_directory, urlquote(ctx or '___', safe=''))

    def _max_rev(self, ctxdir):
        try:
            return max(int(x.group('index')) for x in (STORE_PICKLE_FNAME_REGEX.match(p) for p in listdir(ctxdir)) if x)
        except ValueError:
            return 0

    def _merge(self, ctx, store, triplepat=(None, None, None)):
        ctxdir = self._format_context_directory_name(ctx)
        if not isdir(ctxdir):
            return False
        pickles = (x for x in (STORE_PICKLE_FNAME_REGEX.match(p) for p in listdir(ctxdir)) if x)
        for pickle_match_data in sorted(pickles, key=lambda x: int(x.group('index'))):
            fname = pickle_match_data.group(0)
            with open(p(ctxdir, fname), 'rb') as f:
                try:
                    revision = pickle.load(f)
                except Exception:
                    L.error("Error while unpickling ≪%s≫", p(ctxdir, fname))
                    raise

            store_type = pickle_match_data.group('type')
            if store_type == 'a':
                for trip, ctxs in revision.triples(triplepat):
                    store.add(trip, context=ctx)
            elif store_type == 'r':
                for trip, ctxs in revision.triples(triplepat):
                    store.remove(trip, context=ctx)
        return True
