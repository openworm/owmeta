from __future__ import print_function

import rdflib as R
import random as RND
import logging

from yarom.graphObject import (GraphObject,
                               GraphObjectQuerier,
                               ComponentTripler)
from yarom.rdfUtils import deserialize_rdflib_term
from yarom.variable import Variable
from yarom.propertyValue import PropertyValue
from yarom.propertyMixins import (ObjectPropertyMixin, DatatypePropertyMixin)
from PyOpenWorm.data import DataUser
import itertools
import hashlib

L = logging.getLogger(__name__)


class _values(list):

    def add(self, v):
        super(_values, self).append(v)


class RealSimpleProperty(object):
    multiple = False
    link = R.URIRef("property")
    linkName = "property"

    def __init__(self, conf, owner):
        self.conf = conf
        self._v = _values()
        self.owner = owner

    def hasValue(self):
        return len(self._v) > 0

    def has_defined_value(self):
        for x in self._v:
            if x.defined:
                return True
        return False

    def set(self, v):
        if not hasattr(v, "idl"):
            v = PropertyValue(v)

        if self not in v.owner_properties:
            v.owner_properties.append(self)

        if self.multiple:
            self._v.add(v)
        else:
            self._v = _values()
            self._v.add(v)

    @property
    def defined_values(self):
        return tuple(x for x in self._v if x.defined)

    @property
    def values(self):
        return self._v

    @property
    def rdf(self):
        return self.conf['rdf.graph']

    def get(self):
        v = Variable("var" + str(id(self)))
        self._v.add(v)
        if self not in v.owner_properties:
            v.owner_properties.append(self)
        results = GraphObjectQuerier(v, self.rdf)()
        v.owner_properties.remove(self)
        self._v.remove(v)
        return itertools.chain(results, self.defined_values)

    def unset(self, v):
        self._v.remove(v)
        v.owner_properties.remove(self)

    def __call__(self, *args, **kwargs):
        # XXX: Copy-pasted from SimpleProperty. I'm a bad person.
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



class _ValueProperty(RealSimpleProperty):

    def __init__(self, conf, owner_property):
        super(_ValueProperty, self).__init__(conf, owner_property)
        self._owner_property = owner_property
        self.rdf_namespace = R.Namespace(
            conf['rdf.namespace']["SimpleProperty"] + "/")
        self.link = self.rdf_namespace["value"]

    @property
    def multiple(self):
        return self._owner_property.multiple

    @property
    def value_rdf_type(self):
        return self._owner_property.value_rdf_type

    @property
    def rdf(self):
        return self._owner_property.rdf

    def __str__(self):
        return "_ValueProperty(" + str(self._owner_property) + ")"


class _ObjectPropertyMixin(ObjectPropertyMixin):

    def set(self, v):
        from .dataObject import DataObject
        if not isinstance(v, (SimpleProperty, DataObject, Variable)):
            raise Exception(
                "An ObjectProperty only accepts DataObject, SimpleProperty"
                "or Variable instances. Got a " + str(type(v)) + " aka " +
                str(type(v).__bases__))
        return super(ObjectPropertyMixin, self).set(v)


class _ObjectVaulueProperty (_ObjectPropertyMixin, _ValueProperty):
    pass


class _DatatypeValueProperty (DatatypePropertyMixin, _ValueProperty):
    pass


class ObjectProperty (_ObjectPropertyMixin, RealSimpleProperty):
    pass


class DatatypeProperty (DatatypePropertyMixin, RealSimpleProperty):
    pass


class SimpleProperty(GraphObject, DataUser):

    """ Adapts a SimpleProperty to the GraphObject interface """

    def __init__(self, owner, resolver, **kwargs):
        super(SimpleProperty, self).__init__(**kwargs)
        self.owner = owner
        self._id = None
        self._variable = R.Variable("V" + str(RND.random()))
        if self.property_type == "ObjectProperty":
            self._pp = _ObjectVaulueProperty(
                conf=self.conf,
                owner_property=self,
                resolver=resolver)
        else:
            self._pp = _DatatypeValueProperty(
                conf=self.conf,
                owner_property=self,
                resolver=resolver)

        self.properties.append(self._pp)
        self._defined_values_cache = None
        self._defined_values_string_cache = None

    def __repr__(self):
        return str(self.linkName) + "=`" \
            + ";".join(str(s) for s in self.defined_values) + "'"

    def __str__(self):
        return str(self.__class__.__name__) + "(" + str(self.idl.n3()) + ")"

    def __hash__(self):
        return hash(self.idl)

    def identifier(self, *args, **kwargs):
        return R.URIRef(self.rdf_namespace[
                        "a" + hashlib.md5(str(self.owner.identifier()) +
                                          str(self.linkName) +
                                          self._defined_values_string)
                        .hexdigest()])

    def set(self, v):
        self._pp.set(v)
        self._defined_values_cache = None

    def unset(self, v):
        self._pp.unset(v)

    def get(self):
        if self._pp.hasValue():
            if self.property_type == 'ObjectProperty':
                return self._pp.values
            else:
                return [deserialize_rdflib_term(x.idl) for x in self._pp.values]
        else:
            return self._pp.get()

    @property
    def values(self):
        return self._pp.values

    @property
    def _defined_values_string(self):
        if self._defined_values_string_cache is None:
            self._defined_values_string_cache = "".join(
                x.identifier().n3() for x in self.defined_values)
        return self._defined_values_string_cache

    @property
    def defined_values(self):
        if self._defined_values_cache is None:
            self._defined_values_cache = sorted(self._pp.defined_values)
        return self._defined_values_cache

    @property
    def defined(self):
        return self.owner.defined and self._pp.has_defined_value()

    def variable(self):
        return self._variable

    def triples(self, *args, **kwargs):
        return ComponentTripler(self)()

    def hasValue(self):
        return self._pp.hasValue()

    def has_defined_value(self):
        return self._pp.has_defined_value()

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
