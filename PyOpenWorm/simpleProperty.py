from __future__ import print_function

import rdflib as R
import logging
from six import with_metaclass

from yarom.graphObject import GraphObject, GraphObjectQuerier

from yarom.mappedProperty import MappedPropertyClass
from yarom.variable import Variable
from yarom.propertyValue import PropertyValue
from yarom.propertyMixins import (ObjectPropertyMixin,
                                  DatatypePropertyMixin,
                                  UnionPropertyMixin)
from PyOpenWorm.data import DataUser
from PyOpenWorm.contextualize import Contextualizable, ContextualizableClass, contextualized_new, contextualize_helper
from PyOpenWorm.statement import Statement
import itertools
from lazy_object_proxy import Proxy

L = logging.getLogger(__name__)


class _values(list):

    def add(self, v):
        super(_values, self).append(v)


class ContextMappedPropertyClass(MappedPropertyClass, Contextualizable, ContextualizableClass):
    def __init__(self, *args, **kwargs):
        super(ContextMappedPropertyClass, self).__init__(*args, **kwargs)
        self.__context = None

    def __call__(self, *args, **kwargs):
        o = super(ContextMappedPropertyClass, self).__call__(*args, **kwargs)
        return o

    @property
    def context(self):
        return self.__context

    @context.setter
    def context(self, newc):
        if self.__context is not None and self.__context != newc:
            raise Exception('Contexts cannot be reassigned for a class')
        self.__context = newc


class _ContextualizableLazyProxy(Proxy, Contextualizable):
    """ Contextualizes its factory for execution """
    def contextualize(self, context):
        assert isinstance(self.__factory__, Contextualizable)
        self.__factory__ = self.__factory__.contextualize(context)
        return self


class _StatementContextRDFObjectFactory(Contextualizable):
    __slots__ = ('context', 'statement')

    def __init__(self, statement):
        self.context = None
        self.statement = statement

    def contextualize(self, context):
        temp = _StatementContextRDFObjectFactory(self.statement)
        temp.context = context
        return temp

    def __call__(self):
        if self.context is None:
            raise ValueError("No context has been set for this proxy")
        return self.statement.context.contextualize(self.context).rdf_object


class RealSimpleProperty(with_metaclass(ContextMappedPropertyClass,
                                        DataUser, Contextualizable)):
    multiple = False
    link = R.URIRef("property")
    linkName = "property"
    base_namespace = R.Namespace("http://openworm.org/entities/")

    def __init__(self, conf, owner):
        self._v = _values()
        self.owner = owner

    def contextualize(self, context):
        # print('contextualizing', self, id(self), context)
        res = contextualize_helper(context, self)
        # print('contextualized', self, 'id(self)', id(self), 'id(res)', id(res), context, res.context)
        return res

    def has_value(self):
        for x in self._v:
            if x.context == self.context:
                return True
        return False

    def has_defined_value(self):
        for x in self._v:
            if x.object.defined:
                if x.context == self.context:
                    return True
                else:
                    print("SKIPPING BECAUSE THE CONTEXT IS WRONG")
        return False

    def set(self, v):
        if v is None:
            raise ValueError('It is not permitted to declare a property to have value the None')
        if not hasattr(v, 'idl'):
            v = PropertyValue(v)

        if not self.multiple:
            self.clear()

        stmt = self._insert_value(v)
        # print('setting', self.linkName)
        # if self.linkName in ('rdf_type_property','translator'):
            # print('setting', self.linkName, 'type(self)', type(self), 'id(self)',
                  # id(self), 'id(self.owner)', id(self.owner), 'id(v)', id(v), 'self.context', self.context)
        self.context.add_statement(stmt)
        return _ContextualizableLazyProxy(_StatementContextRDFObjectFactory(stmt))

    def clear(self):
        for x in self._v:
            assert self in x.object.owner_properties
            x.object.owner_properties.remove(self)
            self._v.remove(x)

    @property
    def defined_values(self):
        return tuple(x.object for x in self._v
                     if x.object.defined and x.context == self.context)

    @property
    def values(self):
        return tuple(x.object for x in self._v if x.context == self.context)

    @property
    def rdf(self):
        return self.conf['rdf.graph']

    @property
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
        stmt = Statement(self.owner, self, v, self.context)
        self._v.add(stmt)
        if id(self) not in (id(x) for x in v.owner_properties):
            v.owner_properties.append(self)
        return stmt

    def _remove_value(self, v):
        assert self in v.owner_properties
        v.owner_properties.remove(self)
        self._v.remove(Statement(self.owner, self, v, self.context))

    def _ensure_fresh_po_cache(self):
        owner = self.owner
        ident = owner.identifier
        if (owner.po_cache is None or owner.po_cache.cache_index !=
                self.conf['rdf.graph.change_counter']):
            owner.po_cache = POCache(
                self.conf['rdf.graph.change_counter'], frozenset(
                    self.rdf.predicate_objects(ident)))

    def unset(self, v):
        self._remove_value(v)

    def __call__(self, *args, **kwargs):
        # print('RealSimpleProperty, __call__', type(self), id(self))
        return _get_or_set(self, *args, **kwargs)

    def __repr__(self):
        return _property_to_string(self)

    def one(self):
        return next(iter(self.get()), None)

    def onedef(self):
        for x in self._v:
            if x.object.defined and x.context == self.context:
                return x.object
        return None

    @classmethod
    def on_mapper_add_class(cls, mapper):
        cls.rdf_type = cls.base_namespace[cls.__name__]
        cls.rdf_namespace = R.Namespace(cls.rdf_type + "/")
        return cls


RealSimpleProperty.__new__ = contextualized_new(RealSimpleProperty)


class POCache(tuple):

    """ The predicate-object cache object """

    _map = dict(cache_index=0, cache=1)

    def __new__(cls, cache_index, cache):
        return super(POCache, cls).__new__(cls, (cache_index, cache))

    def __getattr__(self, n):
        return self[POCache._map[n]]


class _ContextualizingPropertySetMixin(object):
    def set(self, v):
        if isinstance(v, _ContextualizableLazyProxy):
            v = v.contextualize(self.context)
        return super(_ContextualizingPropertySetMixin, self).set(v)


class _ObjectPropertyMixin(ObjectPropertyMixin):

    def set(self, v):
        if not isinstance(v, GraphObject):
            raise Exception(
                "An ObjectProperty only accepts GraphObject instances. Got a " +
                str(type(v)) + " a.k.a. " +
                " or ".join(str(x) for x in type(v).__bases__))
        return super(ObjectPropertyMixin, self).set(v)


class ObjectProperty (_ContextualizingPropertySetMixin, _ObjectPropertyMixin, RealSimpleProperty):

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

    def onedef(self):
        x = super(DatatypeProperty, self).onedef()
        return self._resolver.deserializer(x.identifier) if x is not None else x


class UnionProperty(UnionPropertyMixin, RealSimpleProperty):

    """ A Property that can handle either DataObjects or basic types """
    def get(self):
        r = super(UnionProperty, self).get()
        s = set()
        for x in self.defined_values:
            if isinstance(x, R.Literal):
                s.add(self._resolver.deserializer(x.idl))
        return itertools.chain(r, s)


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
            return next(iter(r), None)


def _property_to_string(self):
    try:
        s = str(self.linkName) + "=`" + \
            ";".join(str(s) for s in self.defined_values) + "'"
    except AttributeError:
        s = str(self.linkName) + '(no defined_values)'
    return s
