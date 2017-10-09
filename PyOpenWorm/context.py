import rdflib
from yarom.mapper import Mapper, UnmappedClassException
from yarom.graphObject import ComponentTripler
from .relationshipProxy import RelationshipProxy

from six.moves.urllib.parse import quote


class context_wrapper(object):
    def __init__(self, *args, **kwargs):
        super(context_wrapper, self).__init__(*args, **kwargs)
        self.context.add_object(self)


class _ContextDOMapper(object):
    """ This is just a wrapper for a Mapper """

    def __init__(self, ctx):
        self._ctx = ctx

    def __call__(self, attr):
        """ Returns the class for the attr """
        ret = self._ctx.mapper.load_class(attr)
        try:
            cls = self._ctx.mapper.lookup_class(attr)
            typ = type(cls)
            ret = typ(self._ctx.key + "_" + cls.__name__,
                      (context_wrapper, cls),
                      dict(context=self._ctx))
        except UnmappedClassException:
            pass
        return ret


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
        self.mapper = Mapper(base_class_names,
                             base_namespace=base_namespace,
                             parent=parent_mapper)

        self.identifier = rdflib.URIRef(self.mapper.base_namespace[quote(key)])
        self.load = _ContextDOMapper(self)

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
            graph.update(self._contents_triples())
        elif hasattr(graph, 'get_context'):
            ident = self.identifier
            ctx = graph.get_context(ident)
            ctx.addN((s, p, o, ctx)
                     for s, p, o in self._contents_triples())
        else:
            graph.addN((s, p, o, graph)
                       for s, p, o in self._contents_triples())

        if hasattr(graph, 'commit'):
            graph.commit()

    def _contents_triples(self):
        ct = ComponentTripler(None, generator=True)
        for obj in self._contents.values():
            if type(obj) == RelationshipProxy:
                obj = obj.unwrapped()
            if id(obj) not in ct.seen:
                ct.start = obj
                for t in ct():
                    yield t
