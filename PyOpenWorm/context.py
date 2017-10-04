from yarom.mapper import Mapper, UnmappedClassException, FCN
import transaction
from yarom.graphObject import ComponentTripler
from .relationshipProxy import RelationshipProxy


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
        ctxs = (self._ctx,)
        while len(ctxs) > 0:
            nextctxs = ()
            for ctx in ctxs:
                try:
                    cls = ctx.mapper.load_class(attr)
                    if FCN(cls) in ctx.mapper.MappedClasses:
                        typ = type(cls)
                        cls = typ(self._ctx.key + "_" + cls.__name__,
                                  (context_wrapper, cls),
                                  dict(context=self._ctx))
                    return cls
                except UnmappedClassException:
                    nextctxs += ctx._parent_contexts
            ctxs = nextctxs
        raise UnmappedClassException(attr)


class Context(object):
    """
    A context. Analogous to an RDF context, with some special sauce
    """

    def __init__(self, key=None, parent_contexts=(), base_class_names=(),
                 **kwargs):
        super(Context, self).__init__(**kwargs)
        """ A set of DataObjects """
        if key is None:
            key = 'Context_' + str(id(self))
        self.key = key
        self._contents = dict()
        self._set_buffer_size = 10000
        self.mapper = Mapper(base_class_names)
        self._parent_contexts = parent_contexts

        self.load = _ContextDOMapper(self)

    def contents(self):
        return self._contents.viewvalues()

    def clear(self):
        self._contents.clear()

    def add_object(self, o):
        self._contents[id(o)] = o

    def add_objects(self, objects):
        self._contents.update((id(o), o) for o in objects)

    def save_context(self):
        if self.conf['rdf.source'] == 'ZODB':
            transaction.commit()
            transaction.begin()
        ctx = self.rdf.get_context(self.identifier())
        ctx.addN((s, p, o, ctx) for s, p, o in self._contents_triples())
        if self.conf['rdf.source'] == 'ZODB':
            transaction.commit()
            transaction.begin()

    def _contents_triples(self):
        ct = ComponentTripler(None, generator=True)
        for obj in self._contents.values():
            if type(obj) == RelationshipProxy:
                obj = obj.unwrapped()
            if id(obj) not in ct.seen:
                ct.start = obj
                for t in ct():
                    yield t
