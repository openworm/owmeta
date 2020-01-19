import logging
from os import makedirs, listdir, scandir, unlink, rename, rmdir
from os.path import join as p, exists, isdir, isfile
import shutil
import pickle
from multiprocessing.pool import Pool
from itertools import chain
from time import time

from yarom.utils import FCN
from rdflib.store import Store
from rdflib.plugins.memory import IOMemory
from rdflib.term import URIRef

from .lazy_store_common import STORE_PICKLE_FNAME_REGEX
from .lazy_store_merge import merge, merge0

L = logging.getLogger(__name__)


def Q(s):
    return s.replace('%', '%25').replace('/', '%2F')


def UQ(s):
    return s.replace('%2F', '/').replace('%25', '%')


POOL = Pool(16)


class LazyDeserializationStore(Store):
    '''
    Uses the `IOMemory` store as an in-memory cache and writes new triples to a pickling of
    the store
    '''

    context_aware = True

    def __init__(self, config=None):
        '''
        Paramaters
        ----------
        config : str or dict
            Base directory where pickles are stored or configuration dict
        '''
        super(LazyDeserializationStore, self).__init__(config)

    def open(self, config, create=True):
        if isinstance(config, dict):
            self.__base_directory = config['base_directory']
            self.__max_active = config.get('max_active_contexts', 200)
        elif isinstance(config, str):
            self.__base_directory = config
            self.__max_active = 200
        else:
            raise Exception('Unrecognized configuration')

        self.__tentative_stores = dict()
        self.__removal_stores = dict()

        # A dictionary of contexts to collapse
        self.__should_collapse = dict()
        if not isdir(self.__base_directory):
            if create:
                makedirs(self.__base_directory, exist_ok=True)
            else:
                raise Exception('Base directory does not exist and `create` is not True')
        try:
            active_store_fname = p(self.__base_directory, 'active_store')
            with open(active_store_fname, 'rb') as f:
                (self.__active_store,
                 self.__earliest_revisions,
                 self.__latest_revisions,
                 self.__lru,
                 self.__changenum) = pickle.load(f)
        except FileNotFoundError:
            self.__active_store = dict()
            self.__latest_revisions = dict()
            self.__earliest_revisions = dict()
            self.__lru = dict()
            self.__changenum = 0

        self.__modification_listeners = []

    def close(self, commit_pending_transaction=False):
        if commit_pending_transaction:
            self.commit()

    def destroy(self):
        shutil.rmtree(self.__base_directory)

    def add(self, triple, context=None, quoted=False):
        ctx = getattr(context, 'identifier', context)
        ctx_store = self.__tentative_stores.get(ctx)
        if ctx_store is None:
            ctx_store = self.__tentative_stores.setdefault(ctx, IOMemory())
        ctx_store.add(triple, ctx, quoted)
        self.__changenum += 1
        self.__lru[ctx] = self.__changenum
        self._tpc_register()

    def watch_for_modifications(self, listener):
        self.__modification_listeners.append(listener)

    def earliest_revision(self, ctx):
        return self.__earliest_revisions.get(ctx)

    def latest_revision(self, ctx):
        return self.__latest_revisions.get(ctx)

    def _tpc_register(self):
        for m in self.__modification_listeners:
            m(self)

    def _merge_to_active_arguments(self, ctxdirname):
        this_ctx = UQ(ctxdirname)
        this_earliest_rev = self.earliest_revision(this_ctx)
        this_end_rev = None if this_earliest_rev is None else this_earliest_rev - 1
        active_store = self.__active_store.get(this_ctx)
        if active_store is None:
            active_store = IOMemory()
        self._tpc_register()
        self.__earliest_revisions[this_ctx] = 0
        return (this_ctx,
                self._format_context_directory_name(this_ctx),
                active_store,
                this_end_rev)

    def _add_to_active(self, ctx):
        self.__active_store[ctx] = active_store = IOMemory()
        self.__changenum += 1
        self.__lru[ctx] = self.__changenum
        lru_sorted = sorted(self.__lru.items(), key=lambda x: x[1])
        while len(self.__active_store) > self.__max_active:
            minelem = lru_sorted.pop(0)
            self.__active_store.pop(minelem[0], None)
            self.__earliest_revisions.pop(minelem[0], None)
            self.__latest_revisions.pop(minelem[0], None)
            self.__lru.pop(minelem[0])
        return active_store

    @property
    def active_stores(self):
        return self.__active_store

    def _merge_all_contexts(self):
        args = [self._merge_to_active_arguments(dirname)
                for dirname in listdir(self.__base_directory)]
        return [x[0] for x in POOL.imap_unordered(merge0, args, 100)]

    def triples(self, triplepat, context=None):
        ctx = getattr(context, 'identifier', context)

        earliest_rev = self.earliest_revision(ctx)
        end_rev = None if earliest_rev is None else earliest_rev - 1
        active_store = self.__active_store.get(ctx)
        if not active_store:
            active_store = self._add_to_active(ctx)
        self._merge(ctx, active_store, end_rev=end_rev)
        self._tpc_register()

        if ctx is None:
            # This is loading in every context available, which can be an arbitrary size
            # and we don't want to keep that in memory, so we just load and query a
            # context at a time.
            stores = self._merge_all_contexts()

            for store in stores:
                if not store:
                    continue
                for m in store.triples(triplepat):
                    # We only make tentative stores for contexts we've previously loaded
                    # (possibly on-demand), so we don't have to check for tentative
                    # removals here.
                    yield m[0], (URIRef(x) for x in m[1])

        self.__changenum += 1
        self.__lru[ctx] = self.__changenum

        active_store = self.__active_store.get(ctx)
        if active_store:
            for trip, ctxs in active_store.triples(triplepat, context=ctx):
                removals = self.__removal_stores.get(ctx)
                if removals:
                    removed = next(removals.triples(trip, context=ctx), None)
                else:
                    removed = False
                if not removed:
                    yield trip, (URIRef(x) for x in ctxs)

        tent = self.__tentative_stores.get(ctx)
        if tent:
            tent_triples = tent.triples(triplepat, context=context)
            for trip, ctxs in tent_triples:
                yield trip, (URIRef(x) for x in ctxs)

    def remove(self, triplepat, context=None):
        ctx = getattr(context, 'identifier', context)
        earliest_rev = self.earliest_revision(ctx)
        end_rev = None if earliest_rev is None else earliest_rev - 1
        active_store = self.__active_store.get(ctx)
        if not active_store:
            # We don't have this store active, but it may have triples
            # that we need to remove. merge it in
            active_store = self._add_to_active(ctx)
        self._merge(ctx, active_store, end_rev=end_rev)
        self.__earliest_revisions[ctx] = 0
        active_store_matches = active_store.triples(triplepat, context=ctx)
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
            if len(tent) == 0:
                del self.__tentative_stores[ctx]
        self.__changenum += 1
        self.__lru[ctx] = self.__changenum
        self._tpc_register()

    def contexts(self, triple=None):
        if triple in (None, (None, None, None)):
            tents = set(self.__tentative_stores.keys())
            for m in self._all_committed_contexts():
                tents.discard(m)
                ctxdir = self._format_context_directory_name(m)
                pickles = list(x for x in (STORE_PICKLE_FNAME_REGEX.match(p)
                                           for p in listdir(ctxdir)) if x)
                if len(pickles) == 1:
                    yield m
                    continue
                merged, _ = self._merge(m)
                if len(merged) > 0:
                    yield m
            for t in tents:
                tentative_store = self.__tentative_stores[t]
                removal_store = self.__removal_stores.get(t)
                if removal_store is None:
                    yield t
                    continue

                for tentative_triple in tentative_store.triples((None, None, None)):
                    for removed in removal_store.triples(tentative_triple):
                        break  # inner loop. go on to the next triple
                    else:  # no break
                        yield t
                        break  # outer loop
        else:
            ac = set(self._all_committed_contexts())
            for c, cstore in self.__active_store.items():
                if cstore.triples(triple):
                    yield c
                    ac.remove(c)
                    break

            for c in ac:
                merged, _ = self._merge(c)
                for _ in merged.triples(triple):
                    yield c
                    break

    def _all_committed_contexts(self):
        for dirent in scandir(self.__base_directory):
            if dirent.name not in ('prep', 'temp') and dirent.is_dir():
                yield URIRef(UQ(dirent.name))

    def collapse(self, context):
        '''
        Collapse the revisions for the given context

        Not a standard `rdflib.store.Store` method.
        '''
        ctx = getattr(context, 'identifier', context)
        self.__should_collapse[URIRef(ctx)] = True

    def commit(self):
        try:
            self.tpc_prepare()
        except BaseException:
            self.tpc_abort()
            raise
        else:
            self.tpc_commit()

    def tpc_prepare(self):
        def handle_add(triple, context):
            active_store = self.__active_store.get(context)
            if active_store is None:
                active_store = self._add_to_active(context)
            active_store.add(triple[0], context=context)
        add_revs = self._dex(self.__tentative_stores, 'a', handle_add)
        # If a context is loaded, then we've already merged it into the active store --
        # just need to write the store to disk
        #
        # If not, then, we'll need to call merge to load the missing revisions, in order
        self.__tentative_stores.clear()

        def handle_remove(triple, context):
            active_store = self.__active_store.get(context)
            if active_store is None:
                active_store = self._add_to_active(context)
            active_store.remove(triple[0], context=context)
        rem_revs = self._dex(self.__removal_stores, 'r', handle_remove)

        for ctx, rev in chain(add_revs.items(), rem_revs.items()):
            if ctx in self.__active_store:
                self.__earliest_revisions.setdefault(ctx, rev)

        self.__latest_revisions.update(add_revs)
        self.__latest_revisions.update(rem_revs)

        for c in self.__should_collapse:
            if self.__should_collapse[c]:
                earliest, rev = self.do_collapse(c)
                if rev is None:
                    self.__latest_revisions[c] = None
                elif self.__latest_revisions[c] == rev - 1:
                    self.__latest_revisions[c] = rev

                if earliest is None:
                    del self.__earliest_revisions[c]
                elif earliest == self.__earliest_revisions[c]:
                    self.__earliest_revisions[c] = rev
        self.__should_collapse.clear()

        makedirs(p(self.__base_directory, 'prep'), exist_ok=True)
        with open(p(self.__base_directory, 'prep', 'active_store'), 'wb') as f:
            pickle.dump((self.__active_store,
                         self.__earliest_revisions,
                         self.__latest_revisions,
                         self.__lru,
                         self.__changenum), f)
        self.__removal_stores.clear()

    def do_collapse(self, ctx):
        store = IOMemory()
        _, (earliest_revision, latest_revision) = self._merge(ctx, store)
        has_triples = next(store.triples((None, None, None), context=ctx), None)
        ctxdir = self._format_context_directory_name(ctx)
        rev = None
        if has_triples:
            tempdir = p(ctxdir, 'temp')
            makedirs(tempdir, exist_ok=True)
            collapsed_basename = '%d.a.pickle' % (latest_revision + 1)
            collapsed_fname = p(tempdir, collapsed_basename)
            with open(collapsed_fname, 'wb') as f:
                pickle.dump(store, f)
            rev = latest_revision + 1
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
        return earliest_revision, rev

    def tpc_commit(self):
        prepdir = p(self.__base_directory, 'prep')
        if not isdir(prepdir):
            return
        for ctx_fname in listdir(prepdir):
            this_ctx = UQ(ctx_fname)
            ctx_prepdir = p(prepdir, ctx_fname)
            if not isdir(ctx_prepdir):
                continue
            for fname in listdir(ctx_prepdir):
                md = STORE_PICKLE_FNAME_REGEX.match(fname)
                if not md:
                    continue
                revision_fname = md.group(0)
                ctxdir = self._format_context_directory_name(this_ctx)
                rename(p(prepdir, ctx_prepdir, revision_fname),
                       p(ctxdir, revision_fname))
                rmdir(ctx_prepdir)
        rename(p(prepdir, 'active_store'),
               p(self.__base_directory, 'active_store'))

        rmdir(prepdir)

    def tpc_abort(self):
        self.__tentative_stores.clear()
        self.__removal_stores.clear()
        self.__active_store.clear()
        self.__earliest_revisions.clear()
        self.__latest_revisions.clear()
        prepdir = p(self.__base_directory, 'prep')

        if isdir(prepdir):
            shutil.rmtree(prepdir)

    def _dex(self, stores, revision_type, callback):
        # TODO: Return an indicator for the given revision being complete...
        revisions = dict()
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
                # We don't recreate a prepared file...assume it's already fully prepped
                continue

            with open(revision_fname, 'wb') as f:
                pickle.dump(store, f)

            revisions[ctx] = max_rev + 1

            for triple in chain((has_triples,), store_triples):
                callback(triple, ctx)
        return revisions

    def _format_context_prep_directory_name(self, ctx):
        return p(self.__base_directory, 'prep', Q(ctx or '___'))

    def _format_context_directory_name(self, ctx):
        return p(self.__base_directory, Q(ctx or '___'))

    def _max_rev(self, ctxdir):
        try:
            return max(int(x.group('index')) for x in (STORE_PICKLE_FNAME_REGEX.match(p) for p in listdir(ctxdir)) if x)
        except ValueError:
            return 0

    def _merge(self, ctx, *args, **kwargs):
        return merge(ctx, self._format_context_directory_name(ctx), *args, **kwargs)

    def __repr__(self):
        return '{}({})'.format(FCN(type(self)), self.__base_directory)
