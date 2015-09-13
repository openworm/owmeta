from __future__ import print_function
import rdflib as R
import random as RND
import logging

from yarom.graphObject import GraphObject, ComponentTripler, GraphObjectQuerier
from yarom.rdfUtils import triples_to_bgp, deserialize_rdflib_term
from yarom.rdfTypeResolver import RDFTypeResolver
from .configure import BadConf
from .simpleProperty import DatatypeProperty, SimpleProperty
from .data import DataUser
from .fakeProperty import FakeProperty

__all__ = [
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


class DataObject(GraphObject, DataUser):

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

    def __init__(self, ident=None, key=None, **kwargs):
        try:
            super(DataObject, self).__init__(**kwargs)
        except BadConf:
            raise Exception(
                "You may need to connect to a database before continuing.")

        self.properties = []
        self.owner_properties = []

        if ident is not None:
            self._id = R.URIRef(ident)
        else:
            # Randomly generate an identifier if the derived class can't
            # come up with one from the start. Ensures we always have something
            # that functions as an identifier
            self._id = None

        if key is not None:
            self.setKey(key)

        self._variable = R.Variable("V" + str(RND.random()))
        DataObject.attach_property_ex(self, RDFTypeProperty)
        self.rdf_type_property.set(self.rdf_type)

    def __repr__(self):
        return DataObject.__str__(self)

    def setKey(self, key):
        if isinstance(key, str):
            self._id = self.make_identifier_direct(key)
        else:
            self._id = self.make_identifier(key)

    def make_identifier(self, data):
        import hashlib
        return R.URIRef(
            self.rdf_namespace[
                "a" +
                hashlib.md5(
                    str(data)).hexdigest()])

    def id_is_variable(self):
        """ Is the identifier a variable? """
        return not self.defined

    @classmethod
    def make_identifier_direct(cls, string):
        if not isinstance(string, str):
            raise Exception("make_identifier_direct only accepts strings")
        from urllib import quote
        return R.URIRef(cls.rdf_namespace[quote(string)])

    def triples(self, *args, **kwargs):
        return ComponentTripler(self)()

    def __str__(self):
        s = self.__class__.__name__ + "("
        s += str(self.namespace_manager.normalizeUri(self.idl))
        s += ")"
        return s

    def __eq__(self, other):
        return (isinstance(other, DataObject) and
                (self.identifier() == other.identifier()))

    def load(self):
        for ident in GraphObjectQuerier(self, self.rdf)():
            types = set()
            for rdf_type in self.rdf.objects(ident, R.RDF['type']):
                types.add(rdf_type)
            the_type = get_most_specific_rdf_type(types)
            yield oid(ident, the_type)

    def identifier(self, query=False):
        return self._id

    @property
    def defined(self):
        return self._id is not None

    def variable(self):
        return self._variable

    def __hash__(self):
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
        """ Create a SimpleProperty that has a simple type (string,number,etc)
        as its value

        Parameters
        ----------
        linkName : string
            The name of this Property.
        owner : PyOpenWorm.dataObject.DataObject
            The name of this Property.
        """
        return cls._create_property(
            *args,
            property_type='DatatypeProperty',
            **kwargs)

    @classmethod
    def ObjectProperty(cls, *args, **kwargs):
        """ Create a SimpleProperty that has a complex DataObject as its value

        Parameters
        ----------
        linkName : string
            The name of this Property.
        owner : PyOpenWorm.dataObject.DataObject
            The name of this Property.
        value_type : type
            The type of DataObject for values of this property
        """
        return cls._create_property(
            *args,
            property_type='ObjectProperty',
            **kwargs)

    @classmethod
    def _create_property(
            cls,
            linkName,
            owner,
            property_type,
            value_type=False,
            multiple=False):
        # XXX This should actually get called for all of the properties when
        #     their owner classes are defined. The initialization, however,
        #     must happen with the owner object's creation
        owner_class = cls
        owner_class_name = owner_class.__name__
        property_class_name = owner_class_name + "_" + linkName
        if not value_type:
            value_type = DataObject

        c = None
        if property_class_name in PropertyTypes:
            c = PropertyTypes[property_class_name]
        else:
            if property_type == 'ObjectProperty':
                value_rdf_type = value_type.rdf_type
            else:
                value_rdf_type = False
            link = owner_class.rdf_namespace[linkName]
            c = type(property_class_name,
                     (SimpleProperty,),
                     dict(linkName=linkName,
                          link=link,
                          property_type=property_type,
                          value_rdf_type=value_rdf_type,
                          value_type=value_type,
                          owner_type=owner_class,
                          multiple=multiple))
            PropertyTypes[property_class_name] = c
            c.register()
        return cls.attach_property(owner, c)

    @classmethod
    def register(cls):
        """ Registers the class as a DataObject to be included in the configured rdf graph.
            Puts this class under the control of the database for metadata.

        :return: None
        """
        # NOTE: This expects that configuration has been read in and that the
        # database is available
        assert(issubclass(cls, DataObject))
        DataObjectTypes[cls.__name__] = cls
        DataObjectsParents[
            cls.__name__] = [
            x for x in cls.__bases__ if issubclass(
                x,
                DataObject)]
        cls.parents = DataObjectsParents[cls.__name__]
        cls.rdf_type = cls.conf['rdf.namespace'][cls.__name__]
        RDFTypeTable[cls.rdf_type] = cls
        cls.rdf_namespace = R.Namespace(cls.rdf_type + "/")
        cls.conf['rdf.namespace_manager'].bind(cls.__name__, cls.rdf_namespace)

    @classmethod
    def attach_property_ex(cls, owner, c):
        res = c(owner=owner, conf=owner.conf, resolver=_Resolver.get_instance())
        owner.properties.append(res)
        setattr(owner, c.linkName, res)

        return res

    @classmethod
    def attach_property(self, owner, c):
        # The fake property has the object as owner and the property as value
        res = c(owner=owner, resolver=_Resolver.get_instance())
        # XXX: Hack for graph object traversal of properties while still
        #      allowing to refer to the PyOpenWorm properties.

        fp = FakeProperty(res)
        # ... and the properties of the owner only list the FakeProperty
        owner.properties.append(fp)
        setattr(owner, c.linkName, res)

        return res

    def graph_pattern(self, shorten=False):
        """ Get the graph pattern for this object.

        It should be as simple as converting the result of triples() into a BGP

        Parameters
        ----------
        query : bool
            Indicates whether or not the graph_pattern is to be used for querying
            (as in a SPARQL query) or for storage
        shorten : bool
            Indicates whether to shorten the URLs with the namespace manager
            attached to the ``self``
        """

        nm = None
        if shorten:
            nm = self.namespace_manager
        return triples_to_bgp(self.triples(), namespace_manager=nm)

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
        if not isinstance(identifier_or_rdf_type, R.URIRef):
            identifier_or_rdf_type = R.URIRef(identifier_or_rdf_type)

        if rdf_type is None:
            return oid(identifier_or_rdf_type)
        else:
            rdf_type = R.URIRef(rdf_type)
            return oid(identifier_or_rdf_type, rdf_type)


class RDFTypeProperty(DatatypeProperty):
    link = R.RDF['type']
    linkName = "rdf_type_property"
    owner_type = DataObject
    multiple = True


def oid(identifier_or_rdf_type, rdf_type=None):
    """ Create an object from its rdf type

    Parameters
    ----------
    identifier_or_rdf_type : :class:`str` or :class:`rdflib.term.URIRef`
        If `rdf_type` is provided, then this value is used as the identifier
        for the newly created object. Otherwise, this value will be the
        :attr:`rdf_type` of the object used to determine the Python type and the
        object's identifier will be randomly generated.
    rdf_type : :class:`str`, :class:`rdflib.term.URIRef`, :const:`False`
        If provided, this will be the :attr:`rdf_type` of the newly created object.

    Returns
    -------
       The newly created object

    """
    identifier = identifier_or_rdf_type
    if rdf_type is None:
        rdf_type = identifier_or_rdf_type
        identifier = None

    L.debug("oid making a {} with ident {}".format(rdf_type, identifier))
    c = None
    try:
        c = RDFTypeTable[rdf_type]
    except KeyError:
        c = DataObject

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

    def __init__(self, group_name, **kwargs):
        DataObject.__init__(self, **kwargs)
        self.add = values.ObjectProperty('value', owner=self)
        self.group_name = values.DatatypeProperty('name', owner=self)
        self.name(group_name)

    def identifier(self, query=False):
        return self.make_identifier(self.group_name)


def get_most_specific_rdf_type(types):
    """ Gets the most specific rdf_type.

    Returns the URI corresponding to the lowest in the DataObject class hierarchy
    from among the given URIs.
    """
    most_specific_type = DataObject
    for x in types:
        try:
            class_object = RDFTypeTable[x]
            if issubclass(class_object, most_specific_type):
                most_specific_type = class_object
        except KeyError:
            L.warn(
                """A Python class corresponding to the type URI "{}" couldn't be found.
            You may want to import the module containing the class as well as add additional type
            annotations in order to resolve your objects to a more precise type.""".format(x))
    return most_specific_type.rdf_type


class _Resolver(RDFTypeResolver):
    instance = None

    @classmethod
    def get_instance(cls):
        if cls.instance is None:
            cls.instance = RDFTypeResolver(
                DataObject.rdf_type,
                get_most_specific_rdf_type,
                oid,
                deserialize_rdflib_term)
        return cls.instance
