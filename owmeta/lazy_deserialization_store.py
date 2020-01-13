import logging
from os import makedirs, listdir, scandir, unlink, rename, rmdir
from os.path import join as p, exists, isdir, isfile
import shutil
import pickle
import re
from itertools import chain

from rdflib.store import Store
from rdflib.plugins.memory import IOMemory
from rdflib.term import URIRef

L = logging.getLogger(__name__)

STORE_PICKLE_FNAME_REGEX = re.compile(r'(?P<index>\d+)\.(?P<type>[ra])\.pickle')
''' Regex for the base name of a pickled store '''


def Q(s):
    return s.replace('%', '%25').replace('/', '%2F')


def UQ(s):
    return s.replace('%2F', '/').replace('%25', '%')


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
        self.__tentative_stores = dict()
        self.__removal_stores = dict()

        # A dictionary of contexts to collapse
        self.__should_collapse = dict()
        self.__base_directory = base_directory
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
                 self.__latest_revisions) = pickle.load(f)
        except FileNotFoundError:
            self.__active_store = IOMemory()
            self.__latest_revisions = dict()
            self.__earliest_revisions = dict()

        self.__modification_listeners = []

    def close(self, commit_pending_transaction=False):
        if commit_pending_transaction:
            self.commit()
        self.__base_directory = None

    def add(self, triple, context=None, quoted=False):
        ctx = getattr(context, 'identifier', context)
        ctx_store = self.__tentative_stores.get(ctx)
        if ctx_store is None:
            ctx_store = self.__tentative_stores.setdefault(ctx, IOMemory())
        ctx_store.add(triple, ctx, quoted)
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

    def triples(self, triplepat, context=None):
        ctx = getattr(context, 'identifier', context)

        earliest_rev = self.earliest_revision(ctx)
        end_rev = None if earliest_rev is None else earliest_rev - 1
        self._merge(ctx, self.__active_store, end_rev=end_rev)
        self._tpc_register()

        if ctx is None:
            # This is loading in every context available, which can be an arbitrary size
            # and we don't want to keep that in memory, so we just load and query a
            # context at a time.
            for ctxdirname in listdir(self.__base_directory):
                this_ctx = UQ(ctxdirname)
                this_earliest_rev = self.earliest_revision(this_ctx)
                this_end_rev = None if this_earliest_rev is None else this_earliest_rev - 1
                store, _ = self._merge(this_ctx, self.__active_store, end_rev=this_end_rev)
                self._tpc_register()
                if not store:
                    continue
                for m in store.triples(triplepat):
                    # We only make tentative stores for contexts we've previously loaded
                    # (possibly on-demand), so we don't have to check for tentative
                    # removals here.
                    yield m[0], (URIRef(x) for x in m[1])

        for trip, ctxs in self.__active_store.triples(triplepat, context=ctx):
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
        self._merge(ctx, self.__active_store, end_rev=end_rev)
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
            if len(tent) == 0:
                del self.__tentative_stores[ctx]
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
                    break
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
            for c in self.__active_store.contexts(triple):
                ac.remove(c)
                yield c

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
        add_revs = self._dex(self.__tentative_stores, 'a',
                lambda triple, context: self.__active_store.add(triple[0],
                    context=context))
        # If a context is loaded, then we've already merged it into the active store --
        # just need to write the store to disk
        #
        # If not, then, we'll need to call merge to load the missing revisions, in order
        self.__tentative_stores.clear()
        rem_revs = self._dex(self.__removal_stores, 'r',
                lambda triple, context: self.__active_store.remove(triple[0],
                    context=context))

        for ctx, rev in chain(add_revs.items(), rem_revs.items()):
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
                         self.__latest_revisions), f)
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
        self.__active_store = IOMemory()
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

    def _merge(self, ctx, store=None, triplepat=(None, None, None), start_rev=None, end_rev=None):
        if end_rev is not None and end_rev <= 0:
            return None, None
        ctxdir = self._format_context_directory_name(ctx)
        if not isdir(ctxdir):
            return None, None
        pickles = list(x for x in (STORE_PICKLE_FNAME_REGEX.match(p) for p in listdir(ctxdir)) if x)
        only_one = len(pickles) == 1
        earliest = None
        latest = None
        for pickle_match_data in sorted(pickles, key=lambda x: int(x.group('index'))):
            fname = pickle_match_data.group(0)
            revidx = int(pickle_match_data.group('index'))
            if start_rev is not None and start_rev > revidx:
                continue
            if end_rev is not None and end_rev < revidx:
                continue
            if earliest is None:
                earliest = revidx
            latest = revidx
            with open(p(ctxdir, fname), 'rb') as f:
                try:
                    revision = pickle.load(f)
                except Exception:
                    L.error("Error while unpickling ≪%s≫", p(ctxdir, fname))
                    raise

            if only_one and store is None:
                return revision, (earliest, latest)
            if store is None:
                store = IOMemory()
            store_type = pickle_match_data.group('type')
            if store_type == 'a':
                for trip, ctxs in revision.triples(triplepat):
                    store.add(trip, context=ctx)
            elif store_type == 'r':
                for trip, ctxs in revision.triples(triplepat):
                    store.remove(trip, context=ctx)
        if store is self.__active_store:
            self.__earliest_revisions[ctx] = 0 if start_rev is None else start_rev
        return store, (earliest, latest)
