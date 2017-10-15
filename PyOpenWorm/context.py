import rdflib
from functools import partial
from yarom.mapper import Mapper, UnmappedClassException
from yarom.graphObject import ReferenceTripler
from .relationshipProxy import RelationshipProxy
from .dataObjectUtils import merge_data_objects
from lazy_object_proxy import Proxy

from six.moves.urllib.parse import quote


class _ContextDOMapper(Mapper):
    """ This is just a wrapper for a Mapper """

    def __init__(self, ctx, **kwargs):
        super(_ContextDOMapper, self).__init__(**kwargs)
        self._ctx = ctx

    def decorate_class(self, cls):
        cls.context = self._ctx
        return cls

    def __call__(self, attr):
        """ Returns the class for the attr """
        return  self.load_class(attr)


class Context(object):
    """
    A context. Analogous to an RDF context, with some special sauce
    """

    def __init__(self, key=None, parent=None, base_class_names=(),
                 base_namespace=None,
                 **kwargs):
        super(Context, self).__init__(**kwargs)
        """ A set of DataObjects """
        if key is None:
            key = 'Context_' + str(id(self))
        self.key = key
        self._contents = dict()
        self._set_buffer_size = 10000
        self._parent_context = parent

        parent_mapper = None
        if parent:
            parent_mapper = parent.mapper
        self.mapper = _ContextDOMapper(self,
                                       base_class_names=base_class_names,
                                       base_namespace=base_namespace,
                                       parent=parent_mapper)

        self.identifier = rdflib.URIRef(self.mapper.base_namespace[quote(key)])
        self.load = self.mapper

    def size(self):
        return len(self._contents)

    def contents(self):
        return self._contents.viewvalues()

    def clear(self):
        self._contents.clear()

    def add_object(self, o):
        self._contents[id(o)] = o

    def add_objects(self, objects):
        self._contents.update((id(o), o) for o in objects)

    def save_context(self, graph):
        if hasattr(graph, 'commit'):
            graph.commit()

        if hasattr(graph, 'bind'):
            for c in self.mapper.mapped_classes():
                if hasattr(c, 'rdf_namespace'):
                    graph.bind(c.__name__, c.rdf_namespace)

        if isinstance(graph, set):
            graph.update(self.contents_triples())
        elif hasattr(graph, 'get_context'):
            ident = self.identifier
            ctx = graph.get_context(ident)
            ctx.addN((s, p, o, ctx)
                     for s, p, o in self.contents_triples())
        else:
            graph.addN((s, p, o, graph)
                       for s, p, o in self.contents_triples())

        if hasattr(graph, 'commit'):
            graph.commit()

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
        self.defcnt = 0
        self.tripcnt = 0
        seen_edges = set()
        for obj in self._merged_contents():
            if obj.defined:
                if type(obj) == RelationshipProxy:
                    obj = obj.unwrapped()
                ct = ReferenceTripler(obj)
                ct.seen_edges = seen_edges
                self.defcnt += 1
                for t in ct():
                    self.tripcnt += 1
                    yield t
