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
from lazy_object_proxy import Proxy

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

        if not self.multiple:
            self.clear()

        self._insert_value(v)

        return RelationshipProxy(Rel(self.owner, self, v))

    def clear(self):
        for x in self._v:
            self._remove_value(x)

    @property
    def defined_values(self):
        return tuple(x for x in self._v if x.defined)

    @property
    def values(self):
        return self._v

    @property
    def rdf(self):
        return self.conf['rdf.graph']

    def identifier(self):
        return self.link

    def get(self):
        results = None
        owner = self.owner
        if owner.defined:
            self._ensure_fresh_po_cache()
            results = set()
            for pred, obj in owner.po_cache.cache:
                if pred == self.link:
                    results.add(obj)
        else:
            v = Variable("var" + str(id(self)))
            self._insert_value(v)
            results = GraphObjectQuerier(v, self.rdf, parallel=False)()
            self._remove_value(v)
        return results

    def _insert_value(self, v):
        self._v.add(v)
        if self not in v.owner_properties:
            v.owner_properties.append(self)

    def _remove_value(self, v):
        assert self in v.owner_properties
        v.owner_properties.remove(self)
        self._v.remove(v)

    def _ensure_fresh_po_cache(self):
        owner = self.owner
        ident = owner.identifier()
        if (owner.po_cache is None or owner.po_cache.cache_index !=
                self.conf['rdf.graph.change_counter']):
            owner.po_cache = POCache(
                self.conf['rdf.graph.change_counter'], frozenset(
                    self.rdf.predicate_objects(ident)))

    def unset(self, v):
        self._remove_value(v)

    def __call__(self, *args, **kwargs):
        return _get_or_set(self, *args, **kwargs)

    def __repr__(self):
        return _property_to_string(self)

    def one(self):
        return _next_or_none(self.get())


class POCache(tuple):

    """ The predicate-object cache object """

    _map = dict(cache_index=0, cache=1)

    def __new__(cls, cache_index, cache):
        return super(POCache, cls).__new__(cls, (cache_index, cache))

    def __getattr__(self, n):
        return self[POCache._map[n]]


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
                " or Variable instances. Got a " + str(type(v)) + " aka " +
                str(type(v).__bases__))
        return super(ObjectPropertyMixin, self).set(v)


class _ObjectValueProperty (_ObjectPropertyMixin, _ValueProperty):
    pass


class _DatatypeValueProperty (DatatypePropertyMixin, _ValueProperty):
    pass


class ObjectProperty (_ObjectPropertyMixin, RealSimpleProperty):

    def get(self):
        r = super(ObjectProperty, self).get()
        return itertools.chain(self.defined_values, r)


class DatatypeProperty (DatatypePropertyMixin, RealSimpleProperty):

    def get(self):
        r = super(DatatypeProperty, self).get()
        s = set()
        for x in self.defined_values:
            s.add(self._resolver.deserializer(x.idl))
        return itertools.chain(r, s)


class SimpleProperty(GraphObject, DataUser):

    """ Adapts a SimpleProperty to the GraphObject interface """

    def __init__(self, owner, resolver, **kwargs):
        super(SimpleProperty, self).__init__(**kwargs)
        self.owner = owner
        self._id = None
        self._variable = R.Variable("V" + str(RND.random()))
        if self.property_type == "ObjectProperty":
            self._pp = _ObjectValueProperty(
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
        return _property_to_string(self)

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
        self._defined_values_cache = None
        self._defined_values_string_cache = None
        return self._pp.set(v)

    def unset(self, v):
        self._pp.unset(v)

    def get(self):
        if self._pp.hasValue():
            if self.property_type == 'ObjectProperty':
                return self._pp.values
            else:
                return [deserialize_rdflib_term(x.idl)
                        for x in self._pp.values]
        else:
            return self._pp.get()

    @property
    def values(self):
        return self._pp.values

    @property
    def _defined_values_string(self):
        if self._defined_values_string_cache is None:
            self._defined_values_string_cache = "".join(
                x.identifier().n3().encode('UTF-8')
                for x in self.defined_values)
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
        return _get_or_set(self, *args, **kwargs)

    def one(self):
        return _next_or_none(self.get())

    @classmethod
    def register(cls):
        cls.rdf_type = cls.conf['rdf.namespace'][cls.__name__]
        cls.rdf_namespace = R.Namespace(cls.rdf_type + "/")
        cls.conf['rdf.namespace_manager'].bind(cls.__name__, cls.rdf_namespace)


def _get_or_set(self, *args, **kwargs):
    """ If arguments are given ``set`` method is called. Otherwise, the ``get``
    method is called. If the ``multiple`` member is set to ``True``, then a
    Python set containing the associated values is returned. Otherwise, a
    single bare value is returned.
    """
    # XXX: checking this in advance because I'm paranoid, I guess
    assert hasattr(self, 'set') and hasattr(self.set, '__call__')
    assert hasattr(self, 'get') and hasattr(self.get, '__call__')
    assert hasattr(self, 'multiple')

    if len(args) > 0 or len(kwargs) > 0:
        return self.set(*args, **kwargs)
    else:
        r = self.get(*args, **kwargs)
        if self.multiple:
            return set(r)
        else:
            return _next_or_none(r)


def _next_or_none(r):
    try:
        return next(iter(r))
    except StopIteration:
        return None


def _property_to_string(self):
    assert hasattr(self, 'linkName')
    assert hasattr(self, 'defined_values')
    s = str(self.linkName) + "=`" + \
        ";".join(str(s) for s in self.defined_values) + "'"
    return s


class RelationshipProxy(Proxy):
    def __repr__(self):
        return repr(self.__wrapped__)


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
        from .relationship import Relationship
        return Relationship(
            s=(self.s.idl if self.s.defined else None),
            p=self.p.link,
            o=(self.o.idl if self.o.defined else None))
