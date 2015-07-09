from __future__ import print_function

import rdflib as R
import random as RND
import logging

from yarom.graphObject import GraphObject, GraphObjectQuerier
from yarom.yProperty import Property as P
from yarom.rdfUtils import deserialize_rdflib_term
from yarom.variable import Variable
from yarom.propertyValue import PropertyValue
from PyOpenWorm.v0.simpleProperty import SimpleProperty as SP
from PyOpenWorm.data import DataUser

L = logging.getLogger(__name__)

# TODO: Support ObjectProperty/DatatypeProperty differences a la yarom


class _ValueProperty(object):

    def __init__(self, conf, owner_property):
        self._owner_property = owner_property
        self.conf = conf
        self._v = []
        self.rdf_namespace = R.Namespace(
            conf['rdf.namespace']["SimpleProperty"] + "/")
        self.link = self.rdf_namespace["value"]

    def hasValue(self):
        res = len([x for x in self._v if x.defined]) > 0
        return res

    def set(self, v):
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
    def value_rdf_type(self):
        return self._owner_property.value_rdf_type

    @property
    def rdf(self):
        return self._owner_property.rdf

    def get(self):
        v = Variable("var" + str(id(self)))
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


class _DatatypeProperty(_ValueProperty):

    def set(self, v):
        from .dataObject import DataObject
        if isinstance(v, DataObject):
            L.warn(
                'You are attempting to set a DataObject where a literal is expected.')
        return _ValueProperty.set(self, v)

    def get(self):
        for val in _ValueProperty.get(self):
            yield deserialize_rdflib_term(val)


class _ObjectProperty(_ValueProperty):

    def set(self, v):
        from .dataObject import DataObject
        if not isinstance(v, (DataObject, Variable)):
            raise Exception(
                "An ObjectProperty only accepts DataObject "
                "or Variable instances. Got a " + str(type(v)))
        return _ValueProperty.set(self, v)

    def get(self):
        from .dataObject import DataObject, oid, get_most_specific_rdf_type

        for ident in _ValueProperty.get(self):
            if not isinstance(ident, R.URIRef):
                L.warn(
                    'ObjectProperty.get: Skipping non-URI term, "' +
                    str(ident) +
                    '", returned for a DataObject.')
                continue

            types = set()
            types.add(self.value_rdf_type)

            for rdf_type in self.rdf.objects(ident, R.RDF['type']):
                types.add(rdf_type)

            the_type = get_most_specific_rdf_type(types)
            yield oid(ident, the_type)


class SimpleProperty(GraphObject, DataUser):

    """ Adapts a SimpleProperty to the GraphObject interface """

    def __init__(self, owner):
        GraphObject.__init__(self)
        DataUser.__init__(self)
        self.owner = owner
        self._id = None
        self._variable = R.Variable("V" + str(RND.random()))
        if self.property_type == "ObjectProperty":
            self._pp = _ObjectProperty(self.conf, self)
        else:
            self._pp = _DatatypeProperty(self.conf, self)

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
        if self._pp.hasValue():
            return self._pp.values
        else:
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

    def __call__(self, *args, **kwargs):
        """ If arguments are passed to the ``Property``, its ``set`` method
        is called. Otherwise, the ``get`` method is called. If the ``multiple``
        member for the ``Property`` is set to ``True``, then a Python set containing
        the associated values is returned. Otherwise, a single bare value is returned.
        """

        if len(args) > 0 or len(kwargs) > 0:
            self.set(*args, **kwargs)
            return self
        else:
            r = self.get(*args, **kwargs)
            if self.multiple:
                return set(r)
            else:
                try:
                    return next(iter(r))
                except StopIteration:
                    return None

    def one(self):
        l = list(self.get())
        if len(l) > 0:
            return l[0]
        else:
            return None

    @classmethod
    def register(cls):
        cls.rdf_type = cls.conf['rdf.namespace'][cls.__name__]
        cls.rdf_namespace = R.Namespace(cls.rdf_type + "/")
        cls.conf['rdf.namespace_manager'].bind(cls.__name__, cls.rdf_namespace)
