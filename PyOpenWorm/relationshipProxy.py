from lazy_object_proxy import Proxy


class RelationshipProxy(Proxy):
    def __repr__(self):
        return repr(self.__wrapped__)

    def in_context(self, context):
        rel = self.__factory__
        rel.p.context = context
        return self

    def unwrapped(self):
        return self.__wrapped__


class Rel(tuple):

    """ A container for a relationship-assignment """
    _map = dict(s=0, p=1, o=2)

    def __new__(cls, s, p, o):
        return super(Rel, cls).__new__(cls, (s, p, o))

    def __getattr__(self, n):
        return self[Rel._map[n]]

    def __call__(self):
        return self.rel()

    def rel(self):
        R = self.p.context.load('PyOpenWorm.relationship.Relationship')
        return R(
            s=(self.s if self.s.defined else None),
            p=self.p.rdf_object,
            o=(self.o if self.o.defined else None))
