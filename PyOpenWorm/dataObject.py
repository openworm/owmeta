from __future__ import print_function
from functools import partial
import rdflib as R
from rdflib.term import URIRef
import random as RND
import logging
from itertools import groupby
import six
import hashlib

import PyOpenWorm
from PyOpenWorm.contextualize import (Contextualizable,
                                      ContextualizableClass,
                                      contextualize_metaclass,
                                      contextualize_helper)

from yarom.graphObject import (GraphObject,
                               ComponentTripler,
                               GraphObjectQuerier)
from yarom.rdfUtils import triples_to_bgp, deserialize_rdflib_term
from yarom.rdfTypeResolver import RDFTypeResolver
from yarom.mappedClass import MappedClass
from yarom.mapper import FCN
from .data import DataUser
from .context import Contexts
from .identifier_mixin import IdMixin

from .simpleProperty import ObjectProperty, DatatypeProperty, UnionProperty

__all__ = [
    "BaseDataObject",
    "ContextMappedClass",
    "DataObject",
    "values",
    "DataObjectTypes",
    "RDFTypeTable",
    "DataObjectsParents"]

L = logging.getLogger(__name__)

DataObjectTypes = dict()
PropertyTypes = dict()
RDFTypeTable = dict()
DataObjectsParents = dict()
InverseProperties = dict()


class ContextMappedClass(MappedClass, ContextualizableClass):
    def __init__(self, name, bases, dct):
        super(ContextMappedClass, self).__init__(name, bases, dct)

        ctx_uri = ContextMappedClass._find_class_context(dct, bases)

        if ctx_uri is not None:
            if not isinstance(ctx_uri, URIRef) \
               and isinstance(ctx_uri, (str, six.text_type)):
                ctx_uri = URIRef(ctx_uri)
            self.__context = Contexts[ctx_uri]
        else:
            self.__context = None

        if not hasattr(self, 'base_namespace') or self.base_namespace is None:
            self.base_namespace = ContextMappedClass._find_base_namespace(dct, bases)

    @classmethod
    def _find_class_context(cls, dct, bases):
        ctx_uri = dct.get('class_context', None)
        if ctx_uri is None:
            for b in bases:
                if hasattr(b, 'context') and b.context is not None:
                    ctx_uri = b.context.identifier
                    break

        return ctx_uri

    @classmethod
    def _find_base_namespace(cls, dct, bases):
        base_ns = dct.get('base_namespace', None)
        if base_ns is None:
            for b in bases:
                if hasattr(b, 'base_namespace') and b.base_namespace is not None:
                    base_ns = b.base_namespace
                    break

        return base_ns

    def contextualize_class_augment(self, context):
        if context is None:
            return self
        ctxd_meta = contextualize_metaclass(context, self)
        res = ctxd_meta(self.__name__, (self,), dict(rdf_namespace=self.rdf_namespace,
                                                     rdf_type=self.rdf_type,
                                                     class_context=context.identifier))
        return res

    def after_mapper_module_load(self, mapper):
        if self is not TypeDataObject:
            if self.context is None:
                raise Exception("The class {0} has no context for TypeDataObject(ident={2})".format(
                    self, self.context, self.rdf_type))
            L.debug('Creating rdf_type_object for {} in {}'.format(self, self.context))
            self.rdf_type_object = TypeDataObject.contextualize(self.context)(ident=self.rdf_type)
        else:
            self.rdf_type_object = None

    def __call__(self, *args, **kwargs):
        o = super(ContextMappedClass, self).__call__(*args, **kwargs)

        if isinstance(o, PropertyDataObject):
            o.rdf_type_property(RDFProperty.get_instance())
        elif isinstance(o, RDFProperty):
            o.rdf_type_property(RDFSClass.get_instance())
        elif isinstance(o, RDFSClass):
            o.rdf_type_property.set(o)
        elif isinstance(o, TypeDataObject):
            o.rdf_type_property(RDFSClass.get_instance())
        else:
            o.rdf_type_property.set(self.rdf_type_object)
        return o

    @property
    def context(self):
        return self.__context

    @property
    def definition_context(self):
        """ Unlike self.context, definition_context isn't meant to be overriden """
        return self.__context


class _partial_property(partial):
    pass


def contextualized_data_object(context, obj):
    res = contextualize_helper(context, obj)
    if obj is not res and hasattr(res, 'properties'):
        cprop = res.properties.contextualize(context)
        res.add_attr_override('properties', cprop)
        for p in cprop:
            res.add_attr_override(p.linkName, p)
    return res


class ContextualizableList(Contextualizable, list):

    def __init__(self, context=None):
        self._context = context

    def contextualize(self, context):
        res = type(self)(context=context)
        res += list(x.contextualize(context) for x in self)
        return res


class BaseDataObject(six.with_metaclass(ContextMappedClass,
                                        IdMixin(object, hashfunc=hashlib.md5),
                                        GraphObject,
                                        DataUser,
                                        Contextualizable)):

    """ An object backed by the database

    Attributes
    -----------
    rdf_type : rdflib.term.URIRef
        The RDF type URI for objects of this type
    rdf_namespace : rdflib.namespace.Namespace
        The rdflib namespace (prefix for URIs) for objects from this class
    properties : list of Property
        Properties belonging to this object
    owner_properties : list of Property
        Properties belonging to parents of this object
    """
    rdf_type = R.RDFS['Resource']
    class_context = 'http://openworm.org/schema'
    base_namespace = R.Namespace("http://openworm.org/entities/")

    _next_variable_int = 0

    def __new__(cls, *args, **kwargs):
        """ This is defined so that the __init__ method gets a contextualized
        instance, allowing for statements made in __init__ to be contextualized.
        """
        ores = super(BaseDataObject, cls).__new__(cls)
        if cls.context is not None:
            ores.context = cls.context
            ores.add_contextualization(cls.context, ores)
            res = ores
        else:
            ores.context = None
            res = ores

        return res

    def __init__(self, rdfs_comment=None, rdfs_label=None, **kwargs):
        super(BaseDataObject, self).__init__(**kwargs)
        self.properties = ContextualizableList(context=self.context)
        self.owner_properties = []
        self.po_cache = None
        """ A cache of property URIs and values. Used by RealSimpleProperty """

        self._variable = self.next_variable()
        BaseDataObject.attach_property(self, RDFTypeProperty)
        BaseDataObject.attach_property(self, RDFSCommentProperty)
        BaseDataObject.attach_property(self, RDFSLabelProperty)
        if rdfs_comment:
            self.rdfs_comment = rdfs_comment

        if rdfs_label:
            self.rdfs_label = rdfs_label

    @classmethod
    def next_variable(cls):
        cls._next_variable_int += 1
        return R.Variable('a' + cls.__name__ + '_' + str(DataObject._next_variable_int))

    @property
    def context(self):
        return self.__context

    @context.setter
    def context(self, value):
        self.__context = value

    def clear_po_cache(self):
        """ Clear the property-object cache for this object.

        This cache is maintained by and shared by the properties of this
        object. It isn't necessary to clear this cache manually unless you
        modify the RDFLib graph indirectly (e.g., through the store) at
        runtime.
        """
        self.po_cache = None

    def __repr__(self):
        s = self.__class__.__name__ + "("
        s += 'ident=' + repr(self.idl)
        s += ")"
        return s

    def id_is_variable(self):
        """ Is the identifier a variable? """
        return not self.defined

    def triples(self, *args, **kwargs):
        return ComponentTripler(self, **kwargs)()

    def __str__(self):
        k = self.idl
        if self.namespace_manager is not None:
            k = self.namespace_manager.normalizeUri(k)
        s = self.__class__.__name__ + "("
        s += str(k)
        s += ")"
        return s

    def __eq__(self, other):
        """ This method should not be overridden by subclasses """
        return (isinstance(other, BaseDataObject) and
                self.defined and
                other.defined and
                (self.identifier == other.identifier))

    def __setattr__(self, name, val):
        if isinstance(val, _partial_property):
            val(owner=self, linkName=name)
        else:
            super(BaseDataObject, self).__setattr__(name, val)

    def count(self):
        return len(GraphObjectQuerier(self, self.rdf, parallel=False)())

    def load(self):
        idents = GraphObjectQuerier(self, self.rdf, parallel=False)()
        if idents:
            choices = self.rdf.triples_choices((list(idents),
                                                R.RDF['type'],
                                                None))
            grouped_type_triples = groupby(choices,
                                           lambda x: x[0])
            for ident, type_triples in grouped_type_triples:
                types = set()
                for __, __, rdf_type in type_triples:
                    types.add(rdf_type)
                the_type = get_most_specific_rdf_type(types)
                yield oid(ident, the_type)
        else:
            return

    def variable(self):
        return self._variable

    def __hash__(self):
        """ This method should not be overridden by subclasses """
        return hash(self.idl)

    def __getitem__(self, x):
        try:
            return DataUser.__getitem__(self, x)
        except KeyError:
            raise Exception(
                "You attempted to get the value `%s' from `%s'. It isn't here."
                " Perhaps you misspelled the name of a Property?" %
                (x, self))

    def getOwners(self, property_class_name):
        """ Return the owners along a property pointing to this object """
        res = []
        for x in self.owner_properties:
            if str(x.__class__.__name__) == str(property_class_name):
                res.append(x.owner)
        return res

    # Must resolve, somehow, to a set of triples that we can manipulate
    # For instance, one or more construct query could represent the object or
    # the triples might be stored in memory.
    @classmethod
    def DatatypeProperty(cls, *args, **kwargs):
        """ Attach a, possibly new, property to this class that has a simple
        type (string,number,etc) for its values

        Parameters
        ----------
        linkName : string
            The name of this property.
        owner : PyOpenWorm.dataObject.BaseDataObject
            The name of this property.
        """
        try:
            return cls._create_property(*args, property_type='DatatypeProperty', **kwargs)
        except TypeError:
            return _partial_property(cls._create_property, *args, property_type='DatatypeProperty', **kwargs)

    @classmethod
    def ObjectProperty(cls, *args, **kwargs):
        """ Attach a, possibly new, property to this class that has a complex
        BaseDataObject for its values

        Parameters
        ----------
        linkName : string
            The name of this property.
        owner : PyOpenWorm.dataObject.BaseDataObject
            The name of this property.
        value_type : type
            The type of BaseDataObject for values of this property
        """
        try:
            return cls._create_property(*args, property_type='ObjectProperty', **kwargs)
        except TypeError:
            return _partial_property(cls._create_property, *args, property_type='ObjectProperty', **kwargs)

    @classmethod
    def UnionProperty(cls, *args, **kwargs):
        """ Attach a, possibly new, property to this class that has a simple
        type (string,number,etc) or BaseDataObject for its values

        Parameters
        ----------
        linkName : string
            The name of this property.
        owner : PyOpenWorm.dataObject.BaseDataObject
            The name of this property.
        """
        try:
            return cls._create_property(*args, property_type='UnionProperty', **kwargs)
        except TypeError:
            return _partial_property(cls._create_property, *args, property_type='UnionProperty', **kwargs)

    @classmethod
    def _create_property(
            cls,
            linkName,
            owner,
            property_type,
            value_type=None,
            multiple=False,
            link=None):
        # XXX This should actually get called for all of the properties when
        #     their owner classes are defined. The initialization, however,
        #     must happen with the owner object's creation
        owner_class = cls
        owner_class_name = owner_class.__name__
        property_class_name = str(owner_class_name + "_" + linkName)
        _PropertyTypes_key = (cls, linkName)

        if value_type is None:
            value_type = BaseDataObject

        c = None
        if _PropertyTypes_key in PropertyTypes:
            c = PropertyTypes[_PropertyTypes_key]
        else:
            klass = None
            if property_type == 'ObjectProperty':
                value_rdf_type = value_type.rdf_type
                klass = ObjectProperty
            elif property_type == 'DatatypeProperty':
                value_rdf_type = False
                klass = DatatypeProperty
            elif property_type == 'UnionProperty':
                value_rdf_type = False
                klass = UnionProperty
            else:
                value_rdf_type = False

            if link is None:
                if owner_class.rdf_namespace is None:
                    raise Exception("{}.rdf_namespace is None".format(FCN(owner_class)))
                link = owner_class.rdf_namespace[linkName]
            classes = [klass]
            props = dict(linkName=linkName,
                         link=link,
                         property_type=property_type,
                         value_rdf_type=value_rdf_type,
                         value_type=value_type,
                         owner_type=owner_class,
                         rdf_object=PropertyDataObject.contextualize(owner_class.context)(ident=link),
                         multiple=multiple)

            if _PropertyTypes_key in InverseProperties:
                ip = InverseProperties[_PropertyTypes_key]
                if issubclass(cls, ip.lhs_class) and issubclass(value_type, ip.rhs_class):
                    _class = ip.rhs_class
                    _linkName = ip.rhs_linkName
                elif issubclass(cls, ip.rhs_class) and issubclass(value_type, ip.lhs_class):
                    _class = ip.lhs_class
                    _linkName = ip.lhs_linkName
                else:
                    raise Exception("value_type {} for property ({}, {}) is"
                                    " inconsistent with InverseProperty"
                                    " declaration {}".format(value_type,
                                                             owner_class,
                                                             linkName, ip))
                classes.insert(0, _InversePropertyMixin)

                props['rhs_class'] = _class
                props['rhs_linkName'] = _linkName

            c = type(property_class_name,
                     tuple(classes),
                     props)
            owner_class.mapper.add_class(c)
            PropertyTypes[_PropertyTypes_key] = c
        return cls.attach_property(owner, c)

    @staticmethod
    def attach_property(owner, c):
        ctxd_pclass = c.contextualize(owner.context)
        resolver = _Resolver.get_instance()
        res = ctxd_pclass(owner=owner, conf=owner.conf, resolver=resolver)
        owner.properties.append(res)
        setattr(owner, c.linkName, res)

        return res

    def graph_pattern(self, shorten=False, show_namespaces=True, **kwargs):
        """ Get the graph pattern for this object.

        It should be as simple as converting the result of triples() into a BGP

        Parameters
        ----------
        shorten : bool
            Indicates whether to shorten the URLs with the namespace manager
            attached to the ``self``
        """

        nm = None
        if shorten:
            nm = self.namespace_manager
        return triples_to_bgp(self.triples(**kwargs), namespace_manager=nm,
                              show_namespaces=show_namespaces)

    def retract(self):
        """ Remove this object from the data store. """
        self.retract_statements(self.graph_pattern(query=True))

    def save(self):
        """ Write in-memory data to the database.
        Derived classes should call this to update the store.
        """
        self.add_statements(self.triples())

    @classmethod
    def object_from_id(cls, identifier_or_rdf_type, rdf_type=None):
        if not isinstance(identifier_or_rdf_type, URIRef):
            identifier_or_rdf_type = URIRef(identifier_or_rdf_type)

        if rdf_type is None:
            return oid(identifier_or_rdf_type)
        else:
            rdf_type = URIRef(rdf_type)
            return oid(identifier_or_rdf_type, rdf_type)

    def contextualize_augment(self, context):
        if context is not None:
            return contextualized_data_object(context, self)
        else:
            return self


class DataObject(BaseDataObject):
    pass


class DataObjectSingleton(BaseDataObject):
    instance = None
    class_context = URIRef('http://openworm.org/schema')

    def __init__(self, *args, **kwargs):
        if self._gettingInstance:
            super(DataObjectSingleton, self).__init__(*args, **kwargs)
        else:
            raise Exception(
                "You must call getInstance to get " +
                type(self).__name__)

    @classmethod
    def get_instance(cls, **kwargs):
        if cls.instance is None:
            cls._gettingInstance = True
            cls.instance = cls(**kwargs)
            cls._gettingInstance = False

        return cls.instance


class TypeDataObject(BaseDataObject):
    class_context = URIRef('http://openworm.org/schema')


class RDFSClass(DataObjectSingleton):  # This maybe becomes a DataObject later

    """ The DataObject corresponding to rdfs:Class """
    # XXX: This class may be changed from a singleton later to facilitate
    #      dumping and reloading the object graph
    rdf_type = R.RDFS['Class']
    auto_mapped = True
    class_context = 'http://www.w3.org/2000/01/rdf-schema'

    def __init__(self, *args, **kwargs):
        super(RDFSClass, self).__init__(ident=R.RDFS["Class"], *args, **kwargs)


class RDFTypeProperty(ObjectProperty):
    link = R.RDF['type']
    linkName = "rdf_type_property"
    value_type = RDFSClass
    owner_type = BaseDataObject
    multiple = True


class RDFSCommentProperty(DatatypeProperty):
    link = R.RDFS['comment']
    linkName = 'rdfs_comment'
    owner_type = BaseDataObject
    multiple = True


class RDFSLabelProperty(DatatypeProperty):
    link = R.RDFS['label']
    linkName = 'rdfs_label'
    owner_type = BaseDataObject
    multiple = True


class RDFProperty(DataObjectSingleton):

    """ The DataObject corresponding to rdf:Property """
    rdf_type = R.RDF['Property']
    class_context = URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns')

    def __init__(self, *args, **kwargs):
        super(RDFProperty, self).__init__(ident=R.RDF["Property"],
                                          *args,
                                          **kwargs)


def oid(identifier_or_rdf_type, rdf_type=None):
    """ Create an object from its rdf type

    Parameters
    ----------
    identifier_or_rdf_type : :class:`str` or :class:`rdflib.term.URIRef`
        If `rdf_type` is provided, then this value is used as the identifier
        for the newly created object. Otherwise, this value will be the
        :attr:`rdf_type` of the object used to determine the Python type and
        the object's identifier will be randomly generated.
    rdf_type : :class:`str`, :class:`rdflib.term.URIRef`, :const:`False`
        If provided, this will be the :attr:`rdf_type` of the newly created
        object.

    Returns
    -------
       The newly created object

    """
    identifier = identifier_or_rdf_type
    if rdf_type is None:
        rdf_type = identifier_or_rdf_type
        identifier = None

    c = None
    try:
        c = PyOpenWorm.CONTEXT.mapper.RDFTypeTable[rdf_type]
    except KeyError:
        c = BaseDataObject
    L.debug("oid: making a {} with ident {}".format(c, identifier))

    # if its our class name, then make our own object
    # if there's a part after that, that's the property name
    o = None
    if identifier is not None:
        o = c(ident=identifier)
    else:
        o = c()
    return o


def disconnect():
    global PropertyTypes
    global DataObjectTypes
    global RDFTypeTable
    global DataObjectsParents
    DataObjectTypes.clear()
    RDFTypeTable.clear()
    DataObjectsParents.clear()
    PropertyTypes.clear()


class values(DataObject):

    """
    A convenience class for working with a collection of objects

    Example::

        v = values('unc-13 neurons and muscles')
        n = P.Neuron()
        m = P.Muscle()
        n.receptor('UNC-13')
        m.receptor('UNC-13')
        for x in n.load():
            v.value(x)
        for x in m.load():
            v.value(x)
        # Save the group for later use
        v.save()
        ...
        # get the list back
        u = values('unc-13 neurons and muscles')
        nm = list(u.value())


    Parameters
    ----------
    group_name : string
        A name of the group of objects

    Attributes
    ----------
    name : DatatypeProperty
        The name of the group of objects
    value : ObjectProperty
        An object in the group
    add : ObjectProperty
        an alias for ``value``

    """

    class_context = URIRef('http://openworm.org/schema')

    def __init__(self, group_name, **kwargs):
        super(values, self).__init__(self, **kwargs)
        self.add = values.ObjectProperty('value', owner=self)
        self.group_name = values.DatatypeProperty('name', owner=self)
        self.name(group_name)

    @property
    def identifier(self):
        return self.make_identifier(self.group_name)


def get_most_specific_rdf_type(types):
    """ Gets the most specific rdf_type.

    Returns the URI corresponding to the lowest in the DataObject class
    hierarchy from among the given URIs.
    """
    mapper = PyOpenWorm.CONTEXT.mapper
    most_specific_types = tuple(mapper.base_classes.values())
    for x in types:
        try:
            class_object = mapper.RDFTypeTable[x]
            if issubclass(class_object, most_specific_types):
                most_specific_types = (class_object,)
        except KeyError:
            L.warning(
                """A Python class corresponding to the type URI "{}" couldn't be found.
            You may want to import the module containing the class as well as
            add additional type annotations in order to resolve your objects to
            a more precise type.""".format(x))
    return most_specific_types[0].rdf_type


class PropertyDataObject(DataObject):

    """ A PropertyDataObject represents the property-as-object.

    Try not to confuse this with the Property class
    """
    rdf_type = R.RDF['Property']
    class_context = URIRef('http://openworm.org/schema')

    def __init__(self, *args, **kwargs):
        super(PropertyDataObject, self).__init__(*args, **kwargs)


class _Resolver(RDFTypeResolver):
    instance = None

    @classmethod
    def get_instance(cls):
        if cls.instance is None:
            cls.instance = RDFTypeResolver(
                BaseDataObject.rdf_type,
                get_most_specific_rdf_type,
                oid,
                deserialize_rdflib_term)
        return cls.instance


class _InversePropertyMixin(object):
    """
    Mixin for inverse properties.

    Augments RealSimpleProperty methods to update inverse properties as well
    """

    def set(self, other):
        assert isinstance(other, self.rhs_class)
        rhs_prop = getattr(other, self.rhs_linkName)
        ctxd_rhs_prop = rhs_prop.contextualize(self.context)
        super(_InversePropertyMixin, ctxd_rhs_prop).set(self.owner)
        return super(_InversePropertyMixin, self).set(other)

    def unset(self, other):
        assert isinstance(other, self.rhs_class)
        rhs_prop = getattr(other, self.rhs_linkName)
        super(_InversePropertyMixin, rhs_prop).unset(self.owner)
        super(_InversePropertyMixin, self).unset(other)


class InverseProperty(object):

    def __init__(self, lhs_class, lhs_linkName,
                 rhs_class, rhs_linkName):
        self.lhs_class = lhs_class
        self.rhs_class = rhs_class

        self.lhs_linkName = lhs_linkName
        self.rhs_linkName = rhs_linkName
        InverseProperties[(lhs_class, lhs_linkName)] = self
        InverseProperties[(rhs_class, rhs_linkName)] = self

    def __repr__(self):
        return 'InverseProperty({},{},{},{})'.format(self.lhs_class,
                                                     self.lhs_linkName,
                                                     self.rhs_class,
                                                     self.rhs_linkName)


__yarom_mapped_classes__ = (BaseDataObject, DataObject, RDFSClass, TypeDataObject, RDFProperty,
                            values, PropertyDataObject)
