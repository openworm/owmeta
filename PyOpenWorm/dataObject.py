from __future__ import print_function
from functools import partial
import rdflib as R
from rdflib.term import URIRef
import logging
import six
import hashlib

import PyOpenWorm  # noqa
from . import BASE_SCHEMA_URL, DEF_CTX
from .contextualize import (Contextualizable,
                            ContextualizableClass,
                            contextualize_helper,
                            decontextualize_helper)
from .context import ClassContext, ContextualizableDataUserMixin

from yarom.graphObject import (GraphObject,
                               ComponentTripler,
                               GraphObjectQuerier)
from yarom.rdfUtils import triples_to_bgp, deserialize_rdflib_term
from yarom.rdfTypeResolver import RDFTypeResolver
from yarom.mappedClass import MappedClass
from yarom.utils import FCN
from .data import DataUser
from .identifier_mixin import IdMixin
from .inverse_property import InverseProperty
from .rdf_query_util import goq_hop_scorer, get_most_specific_rdf_type, oid, load

import PyOpenWorm.simpleProperty as SP

__all__ = [
    "BaseDataObject",
    "ContextMappedClass",
    "DataObject"]

L = logging.getLogger(__name__)


PropertyTypes = dict()

This = object()
""" A reference to be used in class-level property declarations to denote the
    class currently being defined. For example::

        >>> class Person(DataObject):
        ...     parent = ObjectProperty(value_type=This,
        ...                             inverse_of=(This, 'child'))
        ...     child = ObjectProperty(value_type=This)
"""


class PropertyProperty(property):
    def __init__(self, cls, *args):
        super(PropertyProperty, self).__init__(*args)
        self._cls = cls

    def __getattr__(self, attr):
        return getattr(self._cls, attr)

    def __repr__(self):
        return '{}(cls={})'.format(FCN(type(self)), repr(self._cls))


def mp(c, k):
    ak = '_pow_' + k
    if c.lazy:
        def getter(target):
            attr = getattr(target, ak, None)
            if attr is None:
                attr = target.attach_property(c, name=ak)
            return attr
    else:
        def getter(target):
            return getattr(target, ak)

    return PropertyProperty(c, getter)


class PThunk(object):
    def __init__(self):
        self.result = None

    def __call__(self, *args, **kwargs):
        raise NotImplementedError()


class CPThunk(PThunk):
    def __init__(self, c):
        super(CPThunk, self).__init__()
        self.c = c

    def __call__(self, *args, **kwargs):
        self.result = self.c
        return self.c


class APThunk(PThunk):
    def __init__(self, t, args, kwargs):
        super(APThunk, self).__init__()
        self.t = t
        self.args = args
        self.kwargs = kwargs

    def __call__(self, cls, linkName):
        if self.result is None:
            self.result = cls._create_property_class(linkName,
                                                     *self.args,
                                                     property_type=self.t,
                                                     **self.kwargs)
        return self.result

    def __repr__(self):
        return '{}({}{})'.format(self.t, self.args and ',\n'.join(self.args) + ', ' or '',
                                 ',\n'.join(k + '=' + str(v) for k, v in self.kwargs.items()))


class Alias(object):
    def __init__(self, target):
        self.target = target

    def __repr__(self):
        return 'Alias(' + repr(self.target) + ')'


def DatatypeProperty(*args, **kwargs):
    return APThunk('DatatypeProperty', args, kwargs)


def ObjectProperty(*args, **kwargs):
    return APThunk('ObjectProperty', args, kwargs)


def UnionProperty(*args, **kwargs):
    return APThunk('UnionProperty', args, kwargs)


class RDFSClass(GraphObject):

    """ The GraphObject corresponding to rdfs:Class """
    # XXX: This class may be changed from a singleton later to facilitate
    #      dumping and reloading the object graph
    rdf_type = R.RDFS['Class']
    auto_mapped = True
    class_context = 'http://www.w3.org/2000/01/rdf-schema'

    instance = None
    defined = True
    identifier = R.RDFS["Class"]

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super(RDFSClass, cls).__new__(cls)
        return cls.instance


TypeDataObject = None


class ContextMappedClass(MappedClass, ContextualizableClass):
    def __init__(self, name, bases, dct):
        super(ContextMappedClass, self).__init__(name, bases, dct)
        ctx = ContextMappedClass._find_class_context(dct, bases)

        if ctx is not None:
            self.__context = ctx
        else:
            self.__context = None

        if not hasattr(self, 'base_namespace') or self.base_namespace is None:
            self.base_namespace = ContextMappedClass._find_base_namespace(dct, bases)

        self._property_classes = dict()
        for b in bases:
            d = getattr(b, '_property_classes', None)
            if d:
                self._property_classes.update(d)

        for k, v in dct.items():
            if isinstance(v, PThunk):
                c = v(self, k)
                self._property_classes[k] = c
                setattr(self, k, mp(c, k))

        for k, v in dct.items():
            if isinstance(v, Alias):
                setattr(self, k, getattr(self, v.target.result.linkName))
                self._property_classes[k] = v.target.result

        key_properties = dct.get('key_properties')
        if key_properties is not None:
            new_key_properties = []
            for kp in key_properties:
                if isinstance(kp, PThunk):
                    for k, p in self._property_classes.items():
                        if p is kp.result:
                            new_key_properties.append(k)
                            break
                    else:
                        raise Exception(("The provided 'key_properties' entry, {},"
                                " does not appear to be a property").format(kp))
                elif isinstance(kp, PropertyProperty):
                    for k, p in self._property_classes.items():
                        if p is kp._cls:
                            new_key_properties.append(k)
                            break
                    else:
                        raise Exception(("The provided 'key_properties' entry, {},"
                                " does not appear to be a property for this class").format(kp))
                elif isinstance(kp, six.string_types):
                    new_key_properties.append(kp)
                else:
                    raise Exception("The provided 'key_properties' entry does not appear"
                            " to be a property")
            self.key_properties = tuple(new_key_properties)

        self.init_rdf_type_object()

        self.__query_form = None

    @classmethod
    def _find_class_context(cls, dct, bases):
        ctx_or_ctx_uri = dct.get('class_context', None)
        if ctx_or_ctx_uri is None:
            for b in bases:
                pctx = getattr(b, 'definition_context', None)
                if pctx is not None:
                    ctx = pctx
                    break
        else:
            if not isinstance(ctx_or_ctx_uri, URIRef) \
               and isinstance(ctx_or_ctx_uri, (str, six.text_type)):
                ctx_or_ctx_uri = URIRef(ctx_or_ctx_uri)
            if isinstance(ctx_or_ctx_uri, (str, six.text_type)):
                ctx = ClassContext(ctx_or_ctx_uri)
            else:
                ctx = ctx_or_ctx_uri
        return ctx

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
        '''
        For MappedClass, rdf_type and rdf_namespace have special behavior where they can
        be auto-generated based on the class name and base_namespace. We have to pass
        through these values to our "proxy" to avoid this behavior
        '''
        res = super(ContextMappedClass, self).contextualize_class_augment(context,
                rdf_type=self.rdf_type,
                rdf_namespace=self.rdf_namespace)
        res.__module__ = self.__module__
        return res

    def after_mapper_module_load(self, mapper):
        '''
        Called after the module has been loaded. See :class:`PyOpenWorm.mapper.Mapper`
        '''
        self.init_python_class_registry_entries()

    def init_rdf_type_object(self):
        global TypeDataObject
        if self.__name__ == 'BaseDataObject':
            # Skip BaseDataObject during initialization since TypeDataObject won't be available yet
            pass
        elif TypeDataObject is None and self.__name__ == 'TypeDataObject':
            # TypeDataObject may not be resolvable yet, so we have to check by name
            TypeDataObject = self
            # We don't use the rdf_type_object, but see `__call__` below for how we
            self.rdf_type_object = None
            BaseDataObject._init_rdf_type_object()
        else:
            self._init_rdf_type_object()

    @property
    def query(self):
        '''
        Stub. Eventually, creates a proxy that changes how some things behave
        for purposes of querying
        '''
        if self.__query_form is None:
            meta = type(self)
            self.__query_form = meta(self.__name__, (_QueryMixin, self),
                    dict(rdf_type=self.rdf_type,
                         rdf_namespace=self.rdf_namespace))
            self.__query_form.__module__ = self.__module__
        return self.__query_form

    def _init_rdf_type_object(self):

        if not hasattr(self, 'rdf_type_object') or \
                self.rdf_type_object is not None and self.rdf_type_object.identifier != self.rdf_type:
            if self.definition_context is None:
                raise Exception("The class {0} has no context for TypeDataObject(ident={1})".format(
                    self, self.rdf_type))
            L.debug('Creating rdf_type_object for {} in {}'.format(self, self.definition_context))
            rdto = TypeDataObject.contextualize(self.definition_context)(ident=self.rdf_type)
            rdto.attach_property(RDFSSubClassOfProperty)
            for par in self.__bases__:
                prdto = getattr(par, 'rdf_type_object', None)
                if prdto is not None:
                    rdto.rdfs_subclassof_property.set(prdto)
            self.rdf_type_object = rdto

    def init_python_class_registry_entries(self):
        re = RegistryEntry.contextualize(self.definition_context)()
        cd = PythonClassDescription.contextualize(self.definition_context)()

        mo = PythonModule.contextualize(self.definition_context)()
        mo.name(self.__module__)

        cd.module(mo)
        cd.name(self.__name__)

        re.rdf_class(self.rdf_type)
        re.class_description(cd)

    def __call__(self, *args, **kwargs):
        o = super(ContextMappedClass, self).__call__(*args, **kwargs)

        if isinstance(o, TypeDataObject):
            o.rdf_type_property(RDFSClass())
        elif isinstance(o, PropertyDataObject):
            o.rdf_type_property(RDFProperty.get_instance())
        elif isinstance(o, RDFProperty):
            o.rdf_type_property(RDFSClass())
        elif isinstance(o, RDFSClass):
            o.rdf_type_property.set(o)
        else:
            o.rdf_type_property.set(self.rdf_type_object)
        return o

    @property
    def context(self):
        return None

    @property
    def definition_context(self):
        """ Unlike self.context, definition_context isn't meant to be overriden """
        return self.__context


class _QueryMixin(object):
    '''
    Mixin for DataObject types to be used for executing queries. This is optional since queries can be executed with
    plain-old DataObjects. Use of the mixin is, however, recommended.

    Overrides the identifier generation logic. May do other things in the future.
    '''

    query_mode = True
    ''' An indicator that the object is in "query" mode allows for simple adaptations in subclasses.'''

    def defined_augment(self):
        return False


def _make_property(cls, property_type, *args, **kwargs):
    try:
        return cls._create_property(property_type=property_type, *args, **kwargs)
    except TypeError:
        return _partial_property(cls._create_property, property_type=property_type, *args, **kwargs)


class _partial_property(partial):
    pass


def contextualized_data_object(context, obj):
    res = contextualize_helper(context, obj)
    if obj is not res and hasattr(res, 'properties'):
        cprop = res.properties.contextualize(context)
        res.add_attr_override('properties', cprop)
        for p in cprop:
            res.add_attr_override(p.linkName, p)

        ops = res.owner_properties
        new_ops = []
        for p in ops:
            if p.context == context:
                new_ops.append(p)
        ctxd_owner_props = res.owner_properties.contextualize(context)
        res.add_attr_override('owner_properties', ctxd_owner_props)
    return res


class ContextualizableList(Contextualizable, list):

    def __init__(self, context):
        super(ContextualizableList, self).__init__()
        self._context = context

    def contextualize(self, context):
        res = type(self)(context=context)
        res += list(x.contextualize(context) for x in self)
        return res

    def decontextualize(self):
        res = type(self)(None)
        res += list(x.decontextualize() for x in self)
        return res


class ContextFilteringList(Contextualizable, list):
    def __init__(self, context):
        self._context = context

    def __iter__(self):
        for x in super(ContextFilteringList, self).__iter__():
            if self._context is None or x.context == self._context:
                yield x

    def contextualize(self, context):
        res = type(self)(context)
        res += self
        return res

    def decontextualize(self):
        return list(super(ContextFilteringList, self).__iter__())


class BaseDataObject(six.with_metaclass(ContextMappedClass,
                                        IdMixin(hashfunc=hashlib.md5),
                                        GraphObject,
                                        ContextualizableDataUserMixin)):

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
    class_context = BASE_SCHEMA_URL
    base_namespace = R.Namespace("http://openworm.org/entities/")

    _next_variable_int = 0

    properties_are_init_args = True
    ''' If true, then properties defined in the class body can be passed as
        keyword arguments to __init__. For example::

            >>> class A(DataObject):
            ...     p = DatatypeProperty()

            >>> A(p=5)

        If the arguments are written explicitly into the __init__ method
        definition, then no special processing is done.
    '''

    key_properties = None

    query_mode = False

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

    def __init__(self, **kwargs):
        ot = type(self)
        pc = ot._property_classes
        paia = ot.properties_are_init_args
        if paia:
            property_args = [(key, val) for key, val in ((k, kwargs.pop(k, None))
                                                         for k in pc)
                             if val is not None]
        super(BaseDataObject, self).__init__(**kwargs)
        self.properties = ContextualizableList(self.context)
        self.owner_properties = ContextFilteringList(self.context)

        self.po_cache = None
        """ A cache of property URIs and values. Used by RealSimpleProperty """

        self._variable = None

        self.filling = False
        for k, v in pc.items():
            if not v.lazy:
                self.attach_property(v, name='_pow_' + k)

        if paia:
            for k, v in property_args:
                getattr(self, k)(v)

        self.attach_property(RDFTypeProperty)

    @property
    def rdf(self):
        if self.context is not None:
            return self.context.rdf_graph()
        else:
            return super(BaseDataObject, self).rdf

    @classmethod
    def next_variable(cls):
        cls._next_variable_int += 1
        return R.Variable('a' + cls.__name__ + '_' + str(cls._next_variable_int))

    @property
    def context(self):
        return self.__context

    @context.setter
    def context(self, value):
        self.__context = value

    def make_identifier_from_properties(self, names):
        '''
        Creates an identifier from properties
        '''
        sdata = ''
        for n in names:
            prop = getattr(self, n)
            val = prop.defined_values[0]
            sdata += val.identifier.n3()
        return self.make_identifier(sdata)

    def defined_augment(self):
        if self.key_properties is not None:
            for k in self.key_properties:
                attr = getattr(self, k, None)
                if attr is None:
                    raise Exception('Key property "{}" is not available on object'.format(k))
                if not attr.has_defined_value():
                    return False
            return True
        else:
            return super(BaseDataObject, self).defined_augment()

    def identifier_augment(self):
        if self.key_properties is not None:
            return self.make_identifier_from_properties(self.key_properties)
        else:
            return super(BaseDataObject, self).identifier_augment()

    def clear_po_cache(self):
        """ Clear the property-object cache for this object.

        This cache is maintained by and shared by the properties of this
        object. It isn't necessary to clear this cache manually unless you
        modify the RDFLib graph indirectly (e.g., through the store) at
        runtime.
        """
        self.po_cache = None

    def __repr__(self):
        return '{}(ident={})'.format(self.__class__.__name__, repr(self.idl))

    def id_is_variable(self):
        """ Is the identifier a variable? """
        return not self.defined

    def triples(self, *args, **kwargs):
        return ComponentTripler(self, **kwargs)()

    def __str__(self):
        k = self.idl
        if self.namespace_manager is not None:
            k = self.namespace_manager.normalizeUri(k)
        return '{}({})'.format(self.__class__.__name__, k)

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
        return len(GraphObjectQuerier(self, self.rdf, parallel=False,
                                      hop_scorer=goq_hop_scorer)())

    def load(self, graph=None):
        # XXX: May need to rethink this refactor at some point...
        for x in load(self.rdf if graph is None else graph,
                      start=self,
                      target_type=type(self).rdf_type,
                      context=self.context):
            yield x

    def fill(self):
        pass

    def variable(self):
        if self._variable is None:
            self._variable = self.next_variable()
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

    def get_owners(self, property_class_name):
        """ Return a generator of owners along a property pointing to this object """
        for x in self.owner_properties:
            if str(x.__class__.__name__) == str(property_class_name):
                yield x.owner

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
        return _make_property(cls, 'DatatypeProperty', *args, **kwargs)

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
        return _make_property(cls, 'ObjectProperty', *args, **kwargs)

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
        return _make_property(cls, 'UnionProperty', *args, **kwargs)

    @classmethod
    def _create_property_class(
            cls,
            linkName,
            property_type,
            value_type=None,
            value_rdf_type=None,
            multiple=False,
            link=None,
            lazy=True,
            inverse_of=None,
            mixins=(),
            **kwargs):

        owner_class = cls
        owner_class_name = owner_class.__name__
        property_class_name = str(owner_class_name + "_" + linkName)
        _PropertyTypes_key = (cls, linkName)

        if value_type is This:
            value_type = owner_class

        if isinstance(value_type, six.text_type):
            value_type = owner_class.mapper.load_class(value_type)

        if value_type is None:
            value_type = BaseDataObject

        c = None
        if _PropertyTypes_key in PropertyTypes:
            c = PropertyTypes[_PropertyTypes_key]
        else:
            klass = None
            if property_type == "ObjectProperty":
                if value_type is not None and value_rdf_type is None:
                    value_rdf_type = value_type.rdf_type
                klass = SP.ObjectProperty
            else:
                value_rdf_type = None
                if property_type in ('DatatypeProperty', 'UnionProperty'):
                    klass = getattr(SP, property_type)

            if link is None:
                if owner_class.rdf_namespace is None:
                    raise Exception("{}.rdf_namespace is None".format(FCN(owner_class)))
                link = owner_class.rdf_namespace[linkName]

            props = dict(linkName=linkName,
                         link=link,
                         value_rdf_type=value_rdf_type,
                         value_type=value_type,
                         owner_type=owner_class,
                         rdf_object=PropertyDataObject.contextualize(owner_class.definition_context)(ident=link),
                         lazy=lazy,
                         multiple=multiple,
                         inverse_of=inverse_of,
                         **kwargs)

            if inverse_of is not None:
                invc = inverse_of[0]
                if invc is This:
                    invc = owner_class
                InverseProperty(owner_class, linkName, invc, inverse_of[1])

            c = type(property_class_name, mixins + (klass,), props)
            c.__module__ = owner_class.__module__
            if hasattr(owner_class, 'mapper') and owner_class.mapper is not None:
                owner_class.mapper.add_class(c)
            PropertyTypes[_PropertyTypes_key] = c
        return c

    @classmethod
    def _create_property(cls, *args, **kwargs):
        owner = None
        if len(args) == 2:
            owner = args[1]
            args = (args[0],)
        else:
            owner = kwargs.get('owner', None)
            if owner is not None:
                del kwargs['owner']
        attr_name = kwargs.get('attrName')
        if owner is None:
            raise TypeError('No owner')
        return owner.attach_property(cls._create_property_class(*args, **kwargs), name=attr_name)

    def attach_property(self, c, name=None):
        ctxd_pclass = c.contextualize_class(self.context)
        res = ctxd_pclass(owner=self,
                          conf=self.conf,
                          resolver=_Resolver.get_instance())
        self.properties.append(res)
        if name is None:
            name = c.linkName
        setattr(self, name, res)

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

        context = DEF_CTX
        if cls.context is not None:
            context = cls.context

        if rdf_type is None:
            return oid(identifier_or_rdf_type, context=context)
        else:
            rdf_type = URIRef(rdf_type)
            return oid(identifier_or_rdf_type, rdf_type, context=context)

    def decontextualize(self):
        if self.context is None:
            return self
        res = decontextualize_helper(self)
        if self is not res:
            cprop = res.properties.decontextualize()
            res.add_attr_override('properties', cprop)
            for p in cprop:
                res.add_attr_override(p.linkName, p)
        return res

    def contextualize_augment(self, context):
        if context is not None:
            return contextualized_data_object(context, self)
        else:
            return self


class _Resolver(RDFTypeResolver):
    instance = None

    @classmethod
    def get_instance(cls):
        if cls.instance is None:
            cls.instance = cls(
                BaseDataObject.rdf_type,
                get_most_specific_rdf_type,
                oid,
                deserialize_rdflib_term)
        return cls.instance


class RDFTypeProperty(SP.ObjectProperty):
    # XXX: This class is special. It doesn't have its after_mapper_module_load called because that would mess up
    # evaluation order for this module...
    link = R.RDF['type']
    linkName = "rdf_type_property"
    value_rdf_type = R.RDFS['Class']
    owner_type = BaseDataObject
    multiple = True
    lazy = False


class RDFSSubClassOfProperty(SP.ObjectProperty):
    link = R.RDFS.subClassOf
    linkName = 'rdfs_subclassof_property'
    value_type = RDFSClass
    owner_type = RDFSClass
    multiple = True
    lazy = False


class TypeDataObject(BaseDataObject):
    class_context = URIRef(BASE_SCHEMA_URL)


class DataObjectSingletonMeta(type(BaseDataObject)):
    @property
    def context(self):
        return self.definition_context


class DataObjectSingleton(six.with_metaclass(DataObjectSingletonMeta, BaseDataObject)):
    instance = None
    class_context = URIRef(BASE_SCHEMA_URL)

    def __init__(self, *args, **kwargs):
        if self._gettingInstance:
            super(DataObjectSingleton, self).__init__(*args, **kwargs)
        else:
            raise Exception("You must call getInstance to get " + type(self).__name__)

    @classmethod
    def get_instance(cls, **kwargs):
        if cls.instance is None:
            cls._gettingInstance = True
            cls.instance = cls(**kwargs)
            cls._gettingInstance = False

        return cls.instance


class PropertyDataObject(BaseDataObject):

    """ A PropertyDataObject represents the property-as-object.

    Try not to confuse this with the Property class
    """
    rdf_type = R.RDF['Property']
    class_context = URIRef(BASE_SCHEMA_URL)


class RDFSCommentProperty(SP.DatatypeProperty):
    link = R.RDFS['comment']
    linkName = 'rdfs_comment'
    owner_type = BaseDataObject
    multiple = True
    lazy = True


class RDFSLabelProperty(SP.DatatypeProperty):
    link = R.RDFS['label']
    linkName = 'rdfs_label'
    owner_type = BaseDataObject
    multiple = True
    lazy = True


class DataObject(BaseDataObject):
    rdfs_comment = CPThunk(RDFSCommentProperty)
    rdfs_label = CPThunk(RDFSLabelProperty)


class RDFProperty(DataObjectSingleton):

    """ The DataObject corresponding to rdf:Property """
    rdf_type = R.RDF['Property']
    class_context = URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns')

    def __init__(self, *args, **kwargs):
        super(RDFProperty, self).__init__(ident=R.RDF["Property"],
                                          *args,
                                          **kwargs)


def disconnect():
    global PropertyTypes
    PropertyTypes.clear()


class Module(DataObject):
    '''
    Represents a module of code

    Most modern programming languages organize code into importable modules of one kind or another. This is basically
    the nearest level above a *class* in the language.
    '''


class ModuleAccess(DataObject):
    '''
    Describes how to access a module.

    Module access is how a person or automated system brings the module to where it can be imported/included, possibly
    in a subsequent
    '''


class ClassDescription(DataObject):
    '''
    Describes a class in the programming language
    '''

    module = ObjectProperty(value_type=Module)
    ''' The module the class belongs to '''


class RegistryEntry(DataObject):

    '''
    A mapping from a class in the programming language to an RDF class.

    Objects of this type are utilized in the resolution of classes from the RDF graph
    '''

    class_description = ObjectProperty(value_type=ClassDescription)
    ''' The description of the class '''

    rdf_class = DatatypeProperty()
    ''' The RDF type for the class '''

    def defined_augment(self):
        return self.class_description.has_defined_value() and self.rdf_class.has_defined_value()

    def identifier_augment(self):
        return self.make_identifier(self.class_description.defined_values[0].identifier.n3() +
                                    self.rdf_class.defined_values[0].identifier.n3())


class PythonModule(Module):
    '''
    A Python module
    '''

    name = DatatypeProperty(multiple=False)
    ''' The full name of the module '''

    def defined_augment(self):
        return self.name.has_defined_value()

    def identifier_augment(self):
        return self.make_identifier_direct(str(self.name.defined_values[0].identifier))


class PyPIPackage(ModuleAccess):

    '''
    Describes a package hosted on the Python Package Index (PyPI)
    '''

    name = DatatypeProperty()
    version = DatatypeProperty()


class PythonClassDescription(ClassDescription):
    name = DatatypeProperty()
    ''' Local name of the class (i.e., relative to the module name) '''

    def defined_augment(self):
        return self.name.has_defined_value() and self.module.has_defined_value()

    def identifier_augment(self):
        return self.make_identifier(self.name.defined_values[0].identifier.n3() +
                                    self.module.defined_values[0].identifier.n3())


CR_TYPES = frozenset((RegistryEntry, PythonClassDescription, PythonModule))

__yarom_mapped_classes__ = (BaseDataObject, DataObject, RDFSClass, TypeDataObject,
                            RDFProperty, RDFSSubClassOfProperty, PropertyDataObject,
                            RegistryEntry, ModuleAccess, ClassDescription, Module,
                            PythonModule, PyPIPackage, PythonClassDescription)
