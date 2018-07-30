from __future__ import print_function
from types import ModuleType
import rdflib
from rdflib.term import Variable, URIRef
from rdflib.graph import ConjunctiveGraph
import wrapt
from .data import DataUser

from .import_contextualizer import ImportContextualizer
from .context_store import ContextStore, RDFContextStore
from .contextualize import (BaseContextualizable,
                            Contextualizable,
                            ContextualizableClass,
                            ContextualizingProxy,
                            contextualize_metaclass)
from yarom.mapper import FCN
from six.moves.urllib.parse import quote
from six import text_type
import six


class ModuleProxy(wrapt.ObjectProxy):
    def __init__(self, ctx, *args, **kwargs):
        super(ModuleProxy, self).__init__(*args, **kwargs)
        self._self_overrides = dict()
        self._self_ctx = ctx

    def add_attr_override(self, name, override):
        self._self_overrides[name] = override

    def __getattr__(self, name):
        o = self._self_overrides.get(name, None)
        if o is not None:
            return o
        else:
            o = super(ModuleProxy, self).__getattr__(name)
            if isinstance(o, (BaseContextualizable, ContextualizableClass)):
                o = o.contextualize(self._self_ctx)
                self._self_overrides[name] = o
            return o


Contexts = dict()


class ContextMeta(ContextualizableClass):
    @property
    def context(self):
        return None

    @context.setter
    def context(self, v):
        pass

    def contextualize_class_augment(self, context):
        if context is None:
            return self
        ctxd_meta = contextualize_metaclass(context, self)
        return ctxd_meta(self.__name__, (self,), dict(class_context=context.identifier))

    def __call__(self, *args, **kwargs):
        o = super(ContextMeta, self).__call__(*args, **kwargs)
        Contexts[o.identifier] = o
        return o


class Context(six.with_metaclass(ContextMeta, ImportContextualizer, Contextualizable, DataUser)):
    """
    A context. Analogous to an RDF context, with some special sauce
    """

    def __init__(self, key=None,
                 imported=(),
                 ident=None,
                 mapper=None,
                 base_namespace=None,
                 **kwargs):
        super(Context, self).__init__(**kwargs)

        if key is not None and ident is not None:
            raise Exception("Only one of 'key' or 'ident' can be given to Context")
        if key is not None and base_namespace is None:
            raise Exception("If 'key' is given, then 'base_namespace' must also be given to Context")

        if not isinstance(ident, URIRef) \
           and isinstance(ident, (str, text_type)):
            ident = URIRef(ident)

        if not isinstance(base_namespace, rdflib.namespace.Namespace) \
           and isinstance(base_namespace, (str, text_type)):
            base_namespace = rdflib.namespace.Namespace(base_namespace)

        if ident is None and key is not None:
            ident = URIRef(base_namespace[quote(key)])

        if not hasattr(self, 'identifier'):
            self.identifier = ident
        else:
            raise Exception(self)

        self._statements = []
        self._set_buffer_size = 10000
        self._imported_contexts = list(imported)
        self._rdf_object = None
        self._graph = None
        self.mapper = mapper
        self.base_namespace = base_namespace

        self._change_counter = 0
        self._triples_saved = 0

    def contents(self):
        return (x for x in self._statements)

    def clear(self):
        del self._statements[:]

    def add_import(self, context):
        self._imported_contexts.append(context)

    def add_statement(self, stmt):
        if self.identifier != stmt.context.identifier:
            raise ValueError("Cannot add statements from a different context")
        self._graph = None
        self._statements.append(stmt)
        self._change_counter += 1

    def remove_statement(self, stmt):
        self._graph = None
        self._statements.remove(stmt)
        self._change_counter += 1

    def add_object(self, o):
        pass

    def add_objects(self, objects):
        pass

    @property
    def imports(self):
        for x in self._imported_contexts:
            yield x

    def save_imports(self, context, *args, **kwargs):
        self.declare_imports(context)
        context.save_context(*args, **kwargs)

    def declare_imports(self, context):
        for ctx in self._imported_contexts:
            if self.identifier is not None \
                    and ctx.identifier is not None \
                    and not isinstance(ctx.identifier, rdflib.term.BNode):
                context(self.rdf_object).imports(ctx.rdf_object)
                ctx.declare_imports(context)

    def save_context(self, graph=None, inline_imports=False, autocommit=True, saved_contexts=None):
        if saved_contexts is None:
            saved_contexts = set([])

        if (self._change_counter, id(self)) in saved_contexts:
            return

        saved_contexts.add((self._change_counter, id(self)))

        if graph is None:
            graph = self._retreive_configured_graph()

        if autocommit and hasattr(graph, 'commit'):
            graph.commit()

        if inline_imports:
            for ctx in self._imported_contexts:
                ctx.save_context(graph, inline_imports, False, saved_contexts)

        if hasattr(graph, 'bind') and self.mapper is not None:
            for c in self.mapper.mapped_classes():
                if hasattr(c, 'rdf_namespace'):
                    graph.bind(c.__name__, c.rdf_namespace)

        if isinstance(graph, set):
            graph.update(self._save_context_triples())
        else:
            ctx_graph = self.get_target_graph(graph)
            ctx_graph.addN((s, p, o, ctx_graph)
                           for s, p, o
                           in self._save_context_triples())

        if autocommit and hasattr(graph, 'commit'):
            graph.commit()

    @property
    def triples_saved(self):
        return self._triples_saved_helper()

    def _triples_saved_helper(self, seen=None):
        if seen is None:
            seen = set()
        if id(self) in seen:
            return 0
        seen.add(id(self))
        res = self._triples_saved
        for ctx in self._imported_contexts:
            res += ctx._triples_saved_helper(seen)
        return res

    def _save_context_triples(self):
        self._triples_saved = 0
        for x in self._statements:
            t = x.to_triple()
            if not (isinstance(t[0], Variable) or
                    isinstance(t[2], Variable) or
                    isinstance(t[1], Variable)):
                self._triples_saved += 1
                yield t

    def get_target_graph(self, graph):
        res = graph
        if self.identifier is not None:
            if hasattr(graph, 'graph_aware') and graph.graph_aware:
                res = graph.graph(self.identifier)
            elif hasattr(graph, 'context_aware') and graph.context_aware:
                res = graph.get_context(self.identifier)
        return res

    def contents_triples(self):
        for x in self._statements:
            yield x.to_triple()

    def contextualize(self, context):
        return ContextualizingProxy(context, self)

    @property
    def rdf_object(self):
        if self._rdf_object is None:
            from PyOpenWorm.contextDataObject import ContextDataObject
            self._rdf_object = ContextDataObject.contextualize(self.context)(ident=self.identifier)

        return self._rdf_object.contextualize(self.context)

    def __bool__(self):
        return True
    __nonzero__ = __bool__

    def __len__(self):
        return len(self._statements)

    def __call__(self, o=None, *args, **kwargs):
        """
        Parameters
        ----------
        o : object
            The object to contexualize. Defaults to locals()
        """
        if o is None:
            o = kwargs
        elif args:
            o = {x.__name__: x for x in [o] + list(args)}

        if isinstance(o, ModuleType):
            return ModuleProxy(self, o)
        elif isinstance(o, dict):
            return ContextContextManager(self, o)
        elif isinstance(o, BaseContextualizable):
            return o.contextualize(self)
        elif isinstance(o, ContextualizableClass):
            # Yes, you can call contextualize on a class and it'll do the right
            # thing, but let's keep it simple here, okay?
            return o.contextualize_class(self)
        else:
            return o

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return '{}(ident="{}")'.format(FCN(type(self)), getattr(self, 'identifier', '???'))

    def load_graph_from_configured_store(self):
        return ConjunctiveGraph(store=RDFContextStore(self))

    def rdf_graph(self):
        if self._graph is None:
            self._graph = self.load_staged_graph()
        return self._graph

    def load_combined_graph(self):
        return ConjunctiveGraph(store=ContextStore(context=self,
                                                   include_stored=True))

    def load_staged_graph(self):
        return ConjunctiveGraph(store=ContextStore(context=self))

    @property
    def query(self):
        return QueryContext(graph=self.load_combined_graph(),
                            ident=self.identifier)

    @property
    def staged(self):
        return QueryContext(graph=self.load_staged_graph(),
                            ident=self.identifier)

    @property
    def stored(self):
        return QueryContext(graph=self.load_graph_from_configured_store(),
                            ident=self.identifier)

    def _retreive_configured_graph(self):
        try:
            return self.conf['rdf.graph']
        except KeyError:
            raise Exception('No graph was given and configuration has no graph')


class QueryContext(Context):
    def __init__(self, graph, *args, **kwargs):
        super(QueryContext, self).__init__(*args, **kwargs)
        self.__graph = graph

    def rdf_graph(self):
        return self.__graph


class ContextContextManager(object):
    """ The context manager created when Context::__call__ is passed a dict """

    def __init__(self, ctx, to_import):
        self._overrides = dict()
        self._ctx = ctx
        self._backing_dict = to_import
        self.save = self._ctx.save_context

    @property
    def context(self):
        return self._ctx

    def __call__(self, o):
        return self._ctx(o)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def __getattr__(self, name):
        return self.lookup(name)

    def __getitem__(self, key):
        return self.lookup(key)

    def lookup(self, key):
        o = self._overrides.get(key, None)
        if o is not None:
            return o
        else:
            o = self._backing_dict[key]
            if isinstance(o, (BaseContextualizable, ContextualizableClass)):
                o = o.contextualize(self._ctx)
                self._overrides[key] = o
            return o
