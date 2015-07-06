from __future__ import print_function
from yarom.graphObject import GraphObject, GraphObjectQuerier
from yarom.yProperty import Property as P
from yarom.variable import Variable
from yarom.propertyValue import PropertyValue
from PyOpenWorm.v0.simpleProperty import SimpleProperty as SP
from PyOpenWorm.data import DataUser
import rdflib as R
import random as RND


class _ValueProperty(object):
    def __init__(self, conf, owner_property):
        self._owner_property = owner_property
        self.conf = conf
        self._v = []
        self.rdf_namespace = R.Namespace(conf['rdf.namespace']["SimpleProperty"] +"/")
        self.link = self.rdf_namespace["value"]

    def hasValue(self):
        res = len([x for x in self._v if x.defined]) > 0
        return res

    def set(self,v):
        import bisect

        if not hasattr(v, "idl"):
            v = PropertyValue(v)

        if self not in v.owner_properties:
            v.owner_properties.append(self)

        if self.multiple:
            bisect.insort(self._v, v)
        else:
            self._v = [v]

    @property
    def owner(self):
        return self._owner_property

    @property
    def values(self):
        return self._v

    @property
    def multiple(self):
        return self._owner_property.multiple

    @property
    def rdf(self):
        return self._owner_property.rdf

    def get(self):
        v = Variable("var"+str(id(self)))
        self.set(v)
        results = GraphObjectQuerier(v, self.rdf)()
        self.unset(v)
        return results

    def unset(self, v):
        idx = self._v.index(v)
        if idx >= 0:
            actual_val = self._v[idx]
            actual_val.owner_properties.remove(self)
            self._v.remove(actual_val)
        else:
            raise Exception("Can't find value {}".format(v))

class SimpleProperty(GraphObject,DataUser):

    """ Adapts a SimpleProperty to the GraphObject interface """

    def __init__(self, owner):
        GraphObject.__init__(self)
        DataUser.__init__(self)
        self.owner = owner
        self._id = None
        self._variable = R.Variable("V"+str(RND.random()))
        self._pp = _ValueProperty(self.conf, self)
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

    def identifier(self, *args, **kwargs):
        import hashlib
        ident = R.URIRef(self.rdf_namespace["a" +
                                                hashlib.md5(str(self.owner.idl) +
                                                            str(self.linkName) +
                                                            str(self.values)).hexdigest()])
        return ident

    def set(self, v):
        self._pp.set(v)

    def unset(self, v):
        self._pp.unset(v)

    def get(self):
        return self._pp.get()

    @property
    def values(self):
        return self._pp.values

    @property
    def defined(self):
        return (self.owner.defined and self._pp.hasValue())

    def variable(self):
        return self._variable

    def hasValue(self):
        return self._pp.hasValue()

    def __call__(self,*args,**kwargs):
        """ If arguments are passed to the ``Property``, its ``set`` method
        is called. Otherwise, the ``get`` method is called. If the ``multiple``
        member for the ``Property`` is set to ``True``, then a Python set containing
        the associated values is returned. Otherwise, a single bare value is returned.
        """

        if len(args) > 0 or len(kwargs) > 0:
            self.set(*args,**kwargs)
            return self
        else:
            r = self.get(*args,**kwargs)
            if self.multiple:
                return set(r)
            else:
                try:
                    return next(iter(r))
                except StopIteration:
                    return None

    @classmethod
    def register(cls):
        cls.rdf_type = cls.conf['rdf.namespace'][cls.__name__]
        cls.rdf_namespace = R.Namespace(cls.rdf_type + "/")
        cls.conf['rdf.namespace_manager'].bind(cls.__name__, cls.rdf_namespace)
