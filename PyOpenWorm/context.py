from __future__ import print_function
import rdflib
from yarom.mapper import Mapper
from yarom.graphObject import DescendantTripler
from .relationshipProxy import RelationshipProxy
from .dataObjectUtils import merge_data_objects

from six.moves.urllib.parse import quote
from six import text_type
from six import with_metaclass


def _M(ctx, c):
    class _H(type(c)):
        def __init__(self, *args, **kwargs):
            super(_H, self).__init__(*args, **kwargs)
            self.__ctx = ctx

        def __call__(self, *args, **kwargs):
            return super(_H, self).__call__(*args, context=self.__ctx, **kwargs)

        # TODO: Create a wrapper for rdf_type_object in the calling context
        # def __getattr__(self, name):
            # print('gettin', self.__class__.__mro__, name)
            # return super(_H, self).__getattr__(name)

    class _G(with_metaclass(_H, c)):
        rdf_namespace = c.rdf_namespace
        rdf_type = c.rdf_type

    return _G


class _ContextDOMapper(Mapper):
    """ This is just a wrapper for a Mapper """

    def __init__(self, ctx, **kwargs):
        super(_ContextDOMapper, self).__init__(**kwargs)
        self._ctx = ctx
        self._wrapped_classes = dict()

    def decorate_class(self, cls):
        return cls

    def __call__(self, attr):
        """ Returns the class for the attr """
        res = self._wrapped_classes.get(attr, None)
        if res is None:
            c = self.load_class(attr)
            res = _M(self._ctx, c)
            self._wrapped_classes[attr] = res
        return res

    def __repr__(self):
        return "{}(ctx={})".format(type(self).__name__, self._ctx)


class Context(object):
    """
    A context. Analogous to an RDF context, with some special sauce
    """

    contexts = dict()

    @classmethod
    def get_context(cls, uri):
        return cls.contexts[uri]

    def __init__(self, key=None,
                 imported=(),
                 base_class_names=(),
                 ident=None,
                 base_namespace=None,
                 **kwargs):
        super(Context, self).__init__(**kwargs)

        if key is not None and ident is not None:
            raise Exception("Only one of 'key' or 'ident' can be given to Context")
        if key is None and ident is None:
            raise Exception("Either 'key' or 'ident' must not be None for Context")
        if key is not None and base_namespace is None:
            raise Exception("If 'key' is given, then 'base_namespace' must also be given to Context")
        if key is None:
            key = 'Context_' + str(id(self))

        if not isinstance(ident, rdflib.term.URIRef) \
           and isinstance(ident, (str, text_type)):
            ident = rdflib.term.URIRef(ident)

        if not isinstance(base_namespace, rdflib.namespace.Namespace) \
           and isinstance(base_namespace, (str, text_type)):
            base_namespace = rdflib.namespace.Namespace(base_namespace)

        if ident is None:
            ident = rdflib.URIRef(base_namespace[quote(key)])

        self.identifier = ident
        Context.contexts[ident] = self

        self._contents = dict()
        self._set_buffer_size = 10000
        self._imported_contexts = imported

        imported_mappers = tuple(im.mapper for im in imported)
        self.mapper = _ContextDOMapper(self,
                                       base_class_names=base_class_names,
                                       base_namespace=base_namespace,
                                       imported=imported_mappers)

        self.cc = self.mapper.load_class
        self.load = self.mapper

    def size(self):
        return len(self._contents) + sum(x.size()
                                         for x in self._imported_contexts)

    def contents(self):
        return self._contents.viewvalues()

    def clear(self):
        self._contents.clear()

    def add_object(self, o):
        self._contents[id(o)] = o

    def add_objects(self, objects):
        self._contents.update((id(o), o) for o in objects)

    def save_context(self, graph):
        self.tripcnt = 0
        self.defcnt = 0
        for ctx in self._imported_contexts:
            ctx.save_context(graph)
        if hasattr(graph, 'commit'):
            graph.commit()

        if hasattr(graph, 'bind'):
            for c in self.mapper.mapped_classes():
                if hasattr(c, 'rdf_namespace'):
                    graph.bind(c.__name__, c.rdf_namespace)
        if isinstance(graph, set):
            graph.update(self.contents_triples())
        elif hasattr(graph, 'graph'):
            ident = self.identifier
            ctx = graph.graph(ident)
            ctx.addN((s, p, o, ctx)
                     for s, p, o in self.contents_triples())
        elif hasattr(graph, 'context_aware') and graph.context_aware:
            ctx = graph.get_context(self.identifier)
            ctx.addN((s, p, o, ctx)
                     for s, p, o in self.contents_triples())
        else:
            graph.addN((s, p, o, graph)
                       for s, p, o in self.contents_triples())

        if hasattr(graph, 'commit'):
            graph.commit()
        self.tripcnt += sum(x.tripcnt for x in self._imported_contexts)
        self.defcnt += sum(x.defcnt for x in self._imported_contexts)

    def _merged_contents(self):
        newc = dict()
        for k in self._contents.values():
            if k.defined:
                kid = k.identifier()
                prek = newc.get(kid, None)
                if prek:
                    newc[kid] = merge_data_objects(prek, k)
                else:
                    newc[kid] = k
        return newc.values()

    def contents_triples(self):
        seen_edges = set()
        for obj in self._merged_contents():
            if obj.defined:
                if type(obj) == RelationshipProxy:
                    obj = obj.unwrapped()
                ct = DescendantTripler(obj, transitive=False)
                ct.seen_edges = seen_edges
                self.defcnt += 1
                for t in ct():
                    self.tripcnt += 1
                    yield t

    def __str__(self):
        return 'Context(ident="{}")'.format(self.identifier)
