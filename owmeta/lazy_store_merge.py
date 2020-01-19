import logging
from os import listdir
from os.path import join as p, isdir
import pickle

from rdflib.plugins.memory import IOMemory

from .lazy_store_common import STORE_PICKLE_FNAME_REGEX

L = logging.getLogger(__name__)


def merge0(args):
    return merge(*args)


def merge(ctx, ctxdir, store=None, end_rev=None):
    if end_rev is not None and end_rev <= 0:
        return store, None
    if not isdir(ctxdir):
        return store, None
    pickles = list(x for x in (STORE_PICKLE_FNAME_REGEX.match(p) for p in listdir(ctxdir)) if x)
    only_one = len(pickles) == 1
    earliest = None
    latest = None
    for pickle_match_data in sorted(pickles, key=lambda x: int(x.group('index'))):
        fname = pickle_match_data.group(0)
        revidx = int(pickle_match_data.group('index'))
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
            for trip, ctxs in revision.triples((None, None, None)):
                store.add(trip, context=ctx)
        elif store_type == 'r':
            for trip, ctxs in revision.triples((None, None, None)):
                store.remove(trip, context=ctx)
    return store, (earliest, latest)
