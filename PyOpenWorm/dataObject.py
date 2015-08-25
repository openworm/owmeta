from __future__ import print_function
import rdflib as R
import random as RND
import logging

from yarom.graphObject import GraphObject, ComponentTripler, GraphObjectQuerier
from yarom.rdfUtils import triples_to_bgp, deserialize_rdflib_term
from yarom.rdfTypeResolver import RDFTypeResolver
from .v0.dataObject import DataObject as DO
from .v0.dataObject import RDFTypeTable
from .v0.dataObject import disconnect as DODisconnect
from .simpleProperty import DatatypeProperty, SimpleProperty
from .fakeProperty import FakeProperty

L = logging.getLogger(__name__)

PropertyTypes = dict()

class DataObject(GraphObject, DO):

    """ Adapts a DataObject to the GraphObject interface """

    def __init__(self, key=None, *args, **kwargs):
        super(DataObject, self).__init__(**kwargs)
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

    def getOwners(self, property_class_name):
        """ Return the owners along a property pointing to this object """
        res = []
        for x in self.owner_properties:
            if str(x.__class__.__name__) == str(property_class_name):
                res.append(x.owner)
        return res

    @classmethod
    def _create_property(
            cls,
            linkName,
            owner,
            property_type,
            value_type=False,
            multiple=False):
        # XXX This should actually get called for all of the properties when
        #     their owner classes are defined. The initialization, however, must
        #     happen with the owner object's creation
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
        print("graph_pattern", self.__class__.__name__)
        print("graph_pattern",self.triples())
        return triples_to_bgp(self.triples(), namespace_manager=nm)


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
    DODisconnect()
    PropertyTypes.clear()


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


