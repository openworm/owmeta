from __future__ import print_function
from types import ModuleType
import rdflib
import wrapt
from .dataObjectUtils import merge_data_objects
from .import_contextualizer import ImportContextualizer
from .contextualize import Contextualizable, ContextualizableClass, ContextualizingProxy

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
            if isinstance(o, Contextualizable):
                o = o.contextualize(self._self_ctx)
                self._self_overrides[name] = o
            return o


Contexts = dict()


class ContextMeta(ContextualizableClass):
    def __call__(self, *args, **kwargs):
        o = super(ContextMeta, self).__call__(*args, **kwargs)
        Contexts[o.identifier] = o
        return o


class Context(six.with_metaclass(ContextMeta, ImportContextualizer, Contextualizable)):
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

        if not isinstance(ident, rdflib.term.URIRef) \
           and isinstance(ident, (str, text_type)):
            ident = rdflib.term.URIRef(ident)

        if not isinstance(base_namespace, rdflib.namespace.Namespace) \
           and isinstance(base_namespace, (str, text_type)):
            base_namespace = rdflib.namespace.Namespace(base_namespace)

        if ident is None and key is not None:
            ident = rdflib.URIRef(base_namespace[quote(key)])

        if not hasattr(self, 'identifier'):
            self.identifier = ident
        else:
            raise Exception(self)

        self._contents = dict()
        self._statements = []
        self._set_buffer_size = 10000
        self._imported_contexts = list(imported)
        self._rdf_object = None
        self.mapper = mapper
        self.base_namespace = base_namespace

        self.tripcnt = 0
        self.defcnt = 0

    def size(self):
        return len(self._contents) + sum(x.size()
                                         for x in self._imported_contexts)

    def contents(self):
        return self._contents.viewvalues()

    def clear(self):
        self._contents.clear()

    def add_import(self, context):
        self._imported_contexts.append(context)

    def add_statement(self, stmt):
        if self.identifier != stmt.context.identifier:
            raise ValueError("Cannot add statements from a different context")
        self._statements.append(stmt)

    def remove_statement(self, stmt):
        self._statements.remove(stmt)

    def add_object(self, o):
        self._contents[id(o)] = o

    def add_objects(self, objects):
        self._contents.update((id(o), o) for o in objects)

    def save_context(self, graph, inline_imports=False):
        self.tripcnt = 0
        self.defcnt = 0
        for ctx in self._imported_contexts:
            if inline_imports:
                ctx.save_context(graph, inline_imports=inline_imports)
                self.tripcnt += ctx.tripcnt
                self.defcnt += ctx.defcnt

            for cctx in ctx._imported_contexts:
                ctx_graph = self.get_target_graph(graph)
                if ctx.identifier is not None \
                        and cctx.identifier is not None \
                        and not isinstance(cctx.identifier, rdflib.term.BNode):
                    ctx_graph.add((ctx.identifier,
                                   rdflib.URIRef('http://example.com/imports'),
                                   cctx.identifier))

        if hasattr(graph, 'commit'):
            graph.commit()

        if hasattr(graph, 'bind') and self.mapper is not None:
            for c in self.mapper.mapped_classes():
                if hasattr(c, 'rdf_namespace'):
                    graph.bind(c.__name__, c.rdf_namespace)

        if isinstance(graph, set):
            graph.update(self.contents_triples())
        else:
            ctx_graph = self.get_target_graph(graph)
            ctx_graph.addN((s, p, o, ctx_graph)
                           for s, p, o in self.contents_triples())

        if hasattr(graph, 'commit'):
            graph.commit()

    def get_target_graph(self, graph):
        res = graph
        if self.identifier is not None:
            if hasattr(graph, 'graph_aware') and graph.graph_aware:
                res = graph.graph(self.identifier)
            elif hasattr(graph, 'context_aware') and graph.context_aware:
                res = graph.get_context(self.identifier)
        return res

    def _merged_contents(self):
        newc = dict()
        for k in self._contents.values():
            if k.defined:
                kid = k.identifier
                prek = newc.get(kid, None)
                if prek:
                    newc[kid] = merge_data_objects(prek, k)
                else:
                    newc[kid] = k
        return newc.values()

    def contents_triples(self):
        for x in self._statements:
            self.tripcnt += 1
            try:
                yield x.to_triple()
            except Exception as e:
                raise e

    def contextualize(self, context):
        return ContextualizingProxy(context, self)

    @property
    def rdf_object(self):
        if self._rdf_object is None:
            # XXX: This is a hack that works for `Evidence.asserts(a.b(c))`
            # since we have to define the Context's RDF type *somewhere*.
            # Really though, A context's rdf_object should have its type
            # statement defined in some other context which specifically holds
            # context metadata.
            from PyOpenWorm.contextDataObject import ContextDataObject
            if self.context is None:
                raise ValueError("Context is none for rdf_object init {} {} of type {}".format(self,
                                                                                               id(self),
                                                                                               type(self)))
            self._rdf_object = ContextDataObject.contextualize(self.context)(ident=self.identifier)
        return self._rdf_object

    def __call__(self, o=None, **kwargs):
        """
        Parameters
        ----------
        o : object
            The object to contexualize. Defaults to locals()
        """
        if o is None:
            o = kwargs

        if isinstance(o, ModuleType):
            return ModuleProxy(self, o)
        elif isinstance(o, dict):
            return ContextContextManager(self, o)
        elif isinstance(o, Contextualizable):
            return o.contextualize(self)
        else:
            return o

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return 'Context(ident="{}")'.format(self.identifier)


class ContextContextManager(object):
    """ The context manager created when Context::__call__ is passed a dict """

    def __init__(self, ctx, to_import):
        self._overrides = dict()
        self._ctx = ctx
        self._backing_dict = to_import
        self.save = self._ctx.save_context

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
            if isinstance(o, Contextualizable):
                o = o.contextualize(self._ctx)
                self._overrides[key] = o
            return o
