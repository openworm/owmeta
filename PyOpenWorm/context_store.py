from rdflib.store import Store, VALID_STORE, NO_STORE
from rdflib.plugins.memory import IOMemory
from rdflib.term import Variable


class ContextStore(Store):
    context_aware = True

    def __init__(self, identifier=None, context=None, **kwargs):
        """
        Parameters
        ----------
            identifier : rdflib.term.URIRef
                context URI?
        """
        super(ContextStore, self).__init__(identifier=identifier, **kwargs)
        self._memory_store = None
        if context is not None:
            self._init_store(context)

    def open(self, configuration, create=False):
        from .context import Contexts
        ctx = Contexts.get(configuration)
        if ctx is not None:
            self._init_store(ctx)
            return VALID_STORE
        else:
            return NO_STORE

    def _init_store(self, ctx):
        self.ctx = ctx
        if self._memory_store is None:
            self._memory_store = IOMemory()
            self._init_store0(ctx)

    def _init_store0(self, ctx, seen=None):
        if seen is None:
            seen = set()
        ctxid = ctx.identifier
        if ctxid in seen:
            return
        seen.add(ctxid)
        self._memory_store.addN((s, p, o, ctxid)
                                for s, p, o
                                in ctx.contents_triples()
                                if not (isinstance(s, Variable) or
                                        isinstance(p, Variable) or
                                        isinstance(o, Variable)))
        for cctx in ctx.imports:
            self._init_store0(cctx, seen)

    def close(self, commit_pending_transaction=False):
        self.ctx = None
        self._memory_store = None

    # RDF APIs
    def add(self, triple, context, quoted=False):
        raise NotImplementedError("This is a query-only store")

    def addN(self, quads):
        raise NotImplementedError("This is a query-only store")

    def remove(self, triple, context=None):
        raise NotImplementedError("This is a query-only store")

    def triples(self, triple_pattern, context=None):
        context = getattr(context, 'identifier', context)
        if self._memory_store is None:
            raise Exception("Database has not been opened")
        subject, predicate, object = triple_pattern
        return self._memory_store.triples(triple_pattern, context)

    def __len__(self, context=None):
        """
        Number of statements in the store. This should only account for non-
        quoted (asserted) statements if the context is not specified,
        otherwise it should return the number of statements in the formula or
        context given.

        :param context: a graph instance to query or None
        """
        if self._memory_store is None:
            raise Exception("Database has not been opened")
        return len(self._memory_store)

    def contexts(self, triple=None):
        """
        Generator over all contexts in the graph. If triple is specified,
        a generator over all contexts the triple is in.

        if store is graph_aware, may also return empty contexts

        :returns: a generator over Nodes
        """
        if self._memory_store is None:
            raise Exception("Database has not been opened")
        return self._memory_store.contexts(triple)

    def query(self, query, initNs, initBindings, queryGraph, **kwargs):
        """
        If stores provide their own SPARQL implementation, override this.

        queryGraph is None, a URIRef or '__UNION__'
        If None the graph is specified in the query-string/object
        If URIRef it specifies the graph to query,
        If  '__UNION__' the union of all named graphs should be queried
        (This is used by ConjunctiveGraphs
        Values other than None obviously only makes sense for
        context-aware stores.)

        """

        raise NotImplementedError
