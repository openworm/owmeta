from yarom.graphObject import GraphObject
from yarom.yProperty import Property as P
from PyOpenWorm.dataObject import SimpleProperty as SP
import rdflib


class _ValueProperty(P):
    def __init__(self, conf):
        self._v = []
        self.rdf_namespace = rdflib.Namespace(conf['rdf.namespace']["SimpleProperty"] +"/")
        self.link = self.rdf_namespace["value"]

    def hasValue(self):
        return len(self._v) > 0

    def set(self, v):
        self._v.append(v)

    @property
    def values(self):
        return self._v

class SimpleProperty(GraphObject, SP):

    """ Adapts a SimpleProperty to the GraphObject interface """

    def __init__(self, *args, **kwargs):
        GraphObject.__init__(self)
        SP.__init__(self, *args, **kwargs)
        self._pp = _ValueProperty(self.conf)
        self.properties.append(self._pp)

    def __repr__(self):
        s = self.__class__.__name__ + "("
        if self._id is not None:
            s += self._id
        s += ")"
        return s

    def __str__(self):
        return str(self.idl)

    def __hash__(self):
        return hash(self.idl)

    def identifier(self):
        import hashlib
        return rdflib.URIRef(self.rdf_namespace["a" +
                                                hashlib.md5(str(self.owner.idl) +
                                                            str(self.linkName) +
                                                            str(self.values)).hexdigest()])
    def set(self, v):
        #SP.set(self, v)
        self._pp.set(v)

    @property
    def values(self):
        return self._v

    @property
    def defined(self):
        return (self.owner.defined and self._pp.hasValue())

    @property
    def variable(self):
        self._id_variable
