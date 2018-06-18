from PyOpenWorm import connect, config
from PyOpenWorm.context import Context
from PyOpenWorm.neuron import Neuron
from PyOpenWorm.evidence import Evidence
from PyOpenWorm.document import Document
from PyOpenWorm.website import Website


connect(configFile="default.conf")
print('the graph', config('rdf.graph'))


def query_context(graph, qctx):
    trips = qctx.contents_triples()
    lctx = None
    for t in trips:
        ctxs = graph.contexts(t)
        if lctx is None:
            lctx = frozenset(ctxs)
            continue
        if len(lctx) == 0:
            return frozenset()
        else:
            lctx = frozenset(ctxs) & lctx
            if len(lctx) == 0:
                return lctx
    return frozenset() if lctx is None else lctx


qctx = Context()
qctx(Neuron)('AVAL').innexin('UNC-7')
ctxs = query_context(config('rdf.graph'), qctx)
for c in ctxs:
    mqctx = Context()
    print('CONTEXT', c.identifier)
    ev = mqctx.stored(Evidence)()
    ev.supports(Context(ident=c.identifier).rdf_object)
    for x in ev.load():
        ref = x.reference()
        if isinstance(ref, Document):
            print(ref)
            print('AUTHOR:', ref.author())
            print('URI:', ref.uri())
            print('DOI:', ref.doi())
            print('PMID:', ref.pmid())
            print('WBID:', ref.wbid())
            print()
        elif isinstance(ref, Website):
            print(ref)
            print('TITLE:', ref.title())
            print('URL:', ref.url())
            print()
