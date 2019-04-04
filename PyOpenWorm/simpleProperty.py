from __future__ import print_function

import rdflib as R
import logging
from six import with_metaclass

from yarom.graphObject import (GraphObject,
                               GraphObjectQuerier,
                               ZeroOrMoreTQLayer)

from yarom.mappedProperty import MappedPropertyClass
from yarom.variable import Variable
from yarom.propertyValue import PropertyValue
from yarom.propertyMixins import (DatatypePropertyMixin,
                                  UnionPropertyMixin)
from yarom.mapper import FCN
from .data import DataUser
from .contextualize import (Contextualizable, ContextualizableClass,
                            contextualize_helper,
                            decontextualize_helper)
from .context import Context
from .statement import Statement
from .inverse_property import InversePropertyMixin
from .rdf_query_util import goq_hop_scorer, load
from .rdf_go_modifiers import SubClassModifier

import itertools
from lazy_object_proxy import Proxy

L = logging.getLogger(__name__)


class ContextMappedPropertyClass(MappedPropertyClass, ContextualizableClass):
    def __init__(self, *args, **kwargs):
        super(ContextMappedPropertyClass, self).__init__(*args, **kwargs)
        self._cmpc_context = None

    @property
    def context(self):
        return object.__getattribute__(self, '_cmpc_context')

    @context.setter
    def context(self, newc):
        if self._cmpc_context is not None and self._cmpc_context != newc:
            raise Exception('Contexts cannot be reassigned for a class')
        self._cmpc_context = newc


class ContextualizedPropertyValue(PropertyValue):

    @property
    def context(self):
        return None


class _ContextualizableLazyProxy(Proxy, Contextualizable):
    """ Contextualizes its factory for execution """
    def contextualize(self, context):
        assert isinstance(self.__factory__, Contextualizable)
        self.__factory__ = self.__factory__.contextualize(context)
        return self

    def __repr__(self):
        return '{}({})'.format(FCN(type(self)), repr(self.__factory__))


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

    def __repr__(self):
        return '{}({})'.format(FCN(type(self)), repr(self.statement))


class RealSimpleProperty(with_metaclass(ContextMappedPropertyClass,
                                        DataUser, Contextualizable)):
    multiple = False
    link = R.URIRef("property")
    linkName = "property"
    base_namespace = R.Namespace("http://openworm.org/entities/")

    def __init__(self, owner, **kwargs):
        super(RealSimpleProperty, self).__init__(**kwargs)
        self._v = []
        self.owner = owner
        self._hdf = dict()
        self.filling = False

    def contextualize_augment(self, context):
        self._hdf[context] = None
        res = contextualize_helper(context, self)
        if res is not self:
            cowner = context(res.owner)
            res.add_attr_override('owner', cowner)
        return res

    def decontextualize(self):
        self._hdf[self.context] = None
        return decontextualize_helper(self)

    def has_value(self):
        for x in self._v:
            if x.context == self.context:
                return True
        return False

    def has_defined_value(self):
        hdf = self._hdf.get(self.context)
        if hdf is not None:
            return hdf
        for x in self._v:
            if x.context == self.context and x.object.defined:
                self._hdf[self.context] = True
                return True
        return False

    def set(self, v):
        if v is None:
            raise ValueError('It is not permitted to declare a property to have value the None')

        if not hasattr(v, 'idl'):
            v = ContextualizedPropertyValue(v)

        if not self.multiple:
            self.clear()

        stmt = self._insert_value(v)
        if self.context is not None:
            self.context.add_statement(stmt)
        return stmt

    def clear(self):
        """ Clears values set *in all contexts* """
        self._hdf = dict()
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
        return tuple(self._values_helper())

    def _values_helper(self):
        for x in self._v:
            if x.context == self.context:
                # XXX: decontextualzing default context here??
                if self.context is not None:
                    yield self.context(x.object)
                elif isinstance(x.object, Contextualizable):
                    yield x.object.decontextualize()
                else:
                    yield x.object

    @property
    def rdf(self):
        if self.context is not None:
            return self.context.rdf_graph()
        else:
            return super(RealSimpleProperty, self).rdf

    @property
    def identifier(self):
        return self.link

    def fill(self):
        self.filling = True
        try:
            self.clear()
            for val in self.get():
                self.set(val)
                fill = getattr(val, 'fill', True)
                filling = getattr(val, 'filling', True)
                if fill and not filling:
                    fill()
        finally:
            self.filling = False

    def get(self):
        if self.rdf is None:
            return ()
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

            def _zomifier(rdf_type):
                if rdf_type and getattr(self, 'value_rdf_type', None) == rdf_type:
                    return SubClassModifier(rdf_type)
            g = ZeroOrMoreTQLayer(_zomifier, self.rdf)
            results = GraphObjectQuerier(v, g, parallel=False,
                                         hop_scorer=goq_hop_scorer)()
            self._remove_value(v)
        return results

    def _insert_value(self, v):
        stmt = Statement(self.owner, self, v, self.context)
        self._hdf[self.context] = None
        self._v.append(stmt)
        if self not in v.owner_properties:
            v.owner_properties.append(self)
        return stmt

    def _remove_value(self, v):
        assert self in v.owner_properties
        self._hdf[self.context] = None
        v.owner_properties.remove(self)
        self._v.remove(Statement(self.owner, self, v, self.context))

    def _ensure_fresh_po_cache(self):
        owner = self.owner
        ident = owner.identifier
        graph_index = self.conf.get('rdf.graph.change_counter', None)

        if graph_index is None or owner.po_cache is None or owner.po_cache.cache_index != graph_index:
            owner.po_cache = POCache(graph_index, frozenset(self.rdf.predicate_objects(ident)))

    def unset(self, v):
        self._remove_value(v)

    def __call__(self, *args, **kwargs):
        return _get_or_set(self, *args, **kwargs)

    def __repr__(self):
        fcn = FCN(type(self))
        return '{}(owner={})'.format(fcn, repr(self.owner))

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

    @property
    def defined_statements(self):
        return tuple(x for x in self._v
                     if x.object.defined and x.subject.defined)

    @property
    def statements(self):
        return self.rdf.quads((self.owner.idl, self.link, None, None))


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


class OPResolver(object):

    def __init__(self, context):
        self._ctx = context

    def id2ob(self, ident, typ):
        from .rdf_query_util import oid
        return oid(ident, typ, self._ctx)

    @property
    def type_resolver(self):
        from .dataObject import _Resolver
        return _Resolver.get_instance().type_resolver

    @property
    def deserializer(self):
        from .dataObject import _Resolver
        return _Resolver.get_instance().deserializer

    @property
    def base_type(self):
        from .dataObject import _Resolver
        return _Resolver.get_instance().base_type


class PropertyCountMixin(object):
    def count(self):
        return sum(1 for _ in super(PropertyCountMixin, self).get())


class ObjectProperty(InversePropertyMixin,
                     _ContextualizingPropertySetMixin,
                     PropertyCountMixin,
                     RealSimpleProperty):

    def __init__(self, resolver=None, *args, **kwargs):
        super(ObjectProperty, self).__init__(*args, **kwargs)

    def contextualize_augment(self, context):
        res = super(ObjectProperty, self).contextualize_augment(context)
        if self is not res:
            res.add_attr_override('resolver', OPResolver(context))
        return res

    def set(self, v):
        if not isinstance(v, GraphObject):
            raise Exception(
                "An ObjectProperty only accepts GraphObject instances. Got a " +
                str(type(v)) + " a.k.a. " +
                " or ".join(str(x) for x in type(v).__bases__))
        return super(ObjectProperty, self).set(v)

    def get(self):
        idents = super(ObjectProperty, self).get()
        r = load(self.rdf, idents=idents, context=self.context,
                 target_type=self.value_rdf_type)
        return itertools.chain(self.defined_values, r)

    @property
    def statements(self):
        return itertools.chain(self.defined_statements,
                               (Statement(self.owner,
                                          self,
                                          self.id2ob(x[2]),
                                          Context(ident=x[3]))
                                for x in super(ObjectProperty, self).statements))


class DatatypeProperty(DatatypePropertyMixin, PropertyCountMixin, RealSimpleProperty):

    def get(self):
        r = super(DatatypeProperty, self).get()
        s = set()
        unhashables = []
        for x in self.defined_values:
            val = self.resolver.deserializer(x.idl)
            try:
                s.add(val)
            except TypeError as e:
                unhashables.append(val)
                L.info('Unhashable type: %s', e)
        return itertools.chain(r, s, unhashables)

    def onedef(self):
        x = super(DatatypeProperty, self).onedef()
        return self.resolver.deserializer(x.identifier) if x is not None else x

    @property
    def statements(self):
        return itertools.chain(self.defined_statements,
                               (Statement(self.owner,
                                          self,
                                          self.resolver.deserializer(x[2]),
                                          Context(ident=x[3]))
                                for x in super(DatatypeProperty, self).statements))


class UnionProperty(_ContextualizingPropertySetMixin,
                    InversePropertyMixin,
                    UnionPropertyMixin,
                    PropertyCountMixin,
                    RealSimpleProperty):

    """ A Property that can handle either DataObjects or basic types """
    def get(self):
        r = super(UnionProperty, self).get()
        s = set()
        for x in self.defined_values:
            if isinstance(x, R.Literal):
                s.add(self.resolver.deserializer(x.idl))
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
