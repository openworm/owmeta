from itertools import chain
from rdflib.store import Store, VALID_STORE, NO_STORE
from rdflib.plugins.memory import IOMemory
from rdflib.term import Variable
from yarom.rdfUtils import transitive_lookup

from .context_common import CONTEXT_IMPORTS


class ContextStoreException(Exception):
    pass


class ContextStore(Store):
    context_aware = True

    def __init__(self, context=None, include_stored=False, **kwargs):
        """
        Parameters
        ----------
            context : PyOpenWorm.context.Context
                context

        """
        super(ContextStore, self).__init__(**kwargs)
        self._memory_store = None
        self._include_stored = include_stored
        if context is not None:
            self._init_store(context)

    def open(self, configuration, create=False):
        if self.ctx is not None:
            return VALID_STORE
        else:
            return NO_STORE

    def _init_store(self, ctx):
        self.ctx = ctx

        if self._include_stored:
            self._store_store = RDFContextStore(ctx)
        else:
            self._store_store = None

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
        if self._memory_store is None:
            raise ContextStoreException("Database has not been opened")
        context = getattr(context, 'identifier', context)
        context_triples = []
        if self._store_store is not None:
            context_triples.append(self._store_store.triples(triple_pattern,
                                                             context))
        return chain(self._memory_store.triples(triple_pattern, context),
                     *context_triples)

    def __len__(self, context=None):
        """
        Number of statements in the store. This should only account for non-
        quoted (asserted) statements if the context is not specified,
        otherwise it should return the number of statements in the formula or
        context given.

        :param context: a graph instance to query or None

        """
        if self._memory_store is None:
            raise ContextStoreException("Database has not been opened")
        if self._store_store is None:
            return len(self._memory_store)
        else:
            # We don't know which triples may overlap, so we can't return an accurate count without doing something
            # expensive, so we just give up
            raise NotImplementedError()

    def contexts(self, triple=None):
        """
        Generator over all contexts in the graph. If triple is specified,
        a generator over all contexts the triple is in.

        if store is graph_aware, may also return empty contexts

        :returns: a generator over Nodes
        """
        if self._memory_store is None:
            raise ContextStoreException("Database has not been opened")
        seen = set()
        rest = ()

        if self._store_store is not None:
            rest = self._store_store.contexts(triple)

        for ctx in chain(self._memory_store.contexts(triple), rest):
            if ctx in seen:
                continue
            seen.add(ctx)
            yield ctx


class RDFContextStore(Store):
    # Returns triples imported by the given context
    context_aware = True

    def __init__(self, context=None, imports_graph=None, include_imports=True, **kwargs):
        super(RDFContextStore, self).__init__(**kwargs)
        self.__graph = context.rdf
        self.__imports_graph = imports_graph
        self.__store = self.__graph.store
        self.__context = context
        self.__context_transitive_imports = None
        self.__include_imports = include_imports

    def __init_contexts(self):
        if self.__store is not None and self.__context_transitive_imports is None:
            if self.__include_imports:
                imports = transitive_lookup(self.__store,
                                            self.__context.identifier, CONTEXT_IMPORTS, self.__imports_graph)
                self.__context_transitive_imports = imports
            else:
                self.__context_transitive_imports = set([self.__context.identifier])

    def triples(self, pattern, context=None):
        self.__init_contexts()
        for t in self.__store.triples(pattern, context):
            contexts = set(getattr(c, 'identifier', c) for c in t[1])
            if self.__context_transitive_imports:
                inter = self.__context_transitive_imports & contexts
            else:
                # Note that our own identifier is also included in the
                # transitive imports, so if we don't have *any* imports then we
                # fall back to querying across all contexts => we don't filter
                # based on contexts. This is in line with rdflib ConjuctiveGraph
                # semantics
                inter = contexts
            if inter:
                yield t[0], inter

    def contexts(self, triple=None):
        if triple is not None:
            for x in self.triples(triple):
                for c in x[1]:
                    yield getattr(c, 'identifier', c)
        else:
            self.__init_contexts()
            for c in self.__context_transitive_imports:
                yield c

    def namespace(self, prefix):
        return self.__store.namespace(prefix)

    def prefix(self, uri):
        return self.__store.prefix(uri)

    def bind(self, prefix, namespace):
        return self.__store.bind(prefix, namespace)

    def namespaces(self):
        for x in self.__store.namespaces():
            yield x
