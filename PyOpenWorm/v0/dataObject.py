import rdflib as R
from PyOpenWorm.data import DataUser
from PyOpenWorm.configure import BadConf
import traceback
import logging
import random
import struct

__all__ = ["DataObject", "Property", "values", "DataObjectTypes", "RDFTypeTable"]
L = logging.getLogger(__name__)

# in general it should be possible to recover the entire object from its identifier: the object should be representable as a connected graph.
# However, this need not be a connected *RDF* graph. Indeed, graph literals may hold information which can yield triples which are not
# connected by an actual node

def _bnode_to_var(x):
    return "?" + x

def _rdf_identifier_to_gp(x):
    if isinstance(x,R.BNode):
        return _bnode_to_var(x)
    elif isinstance(x,R.URIRef) and DataObject._is_variable(x):
        return DataObject._graph_variable_to_var(x).n3()
    else:
        return x.n3()

def _rdf_literal_to_python(x):
    if isinstance(x, R.Literal):
        x = x.toPython()
        if isinstance(x, R.Literal):
            x = str(x)
    return x

def _triples_to_bgp(trips):
    # XXX: Collisions could result between the variable names of different objects
    g = " .\n".join(" ".join(_rdf_identifier_to_gp(x) for x in y) for y in trips)
    return g

DataObjectTypes = dict()
RDFTypeTable = dict()
_DataObjectsParents = dict()

class DataObject(DataUser):
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

    def __init__(self,ident=False,triples=False,**kwargs):
        try:
            DataUser.__init__(self,**kwargs)
        except BadConf:
            raise Exception("You may need to connect to a database before continuing.")

        if not triples:
            self._triples = []
        else:
            self._triples = triples
        self._is_releasing_triples = False
        self.properties = []
        self.owner_properties = []
        # Used in triples()
        self._id_is_set = False

        v = struct.pack("=2f",random.random(),random.random())

        if ident:
            self._id = R.URIRef(ident)
            self._id_is_set = True
        else:
            # Randomly generate an identifier if the derived class can't
            # come up with one from the start. Ensures we always have something
            # that functions as an identifier
            self._id = self.make_identifier(v)

        cname = self.__class__.__name__
        self._id_variable = self._graph_variable(cname + v.encode('hex'))

    def __eq__(self,other):
        return isinstance(other,DataObject) and (self.identifier() == other.identifier())

    def __str__(self):
        s = self.__class__.__name__ + "("
        s +=  ", ".join(str(x) for x in self.properties if x.hasValue())
        s += ")"
        return s

    def __repr__(self):
        return self.__str__()

    def _graph_variable(self,var_name):
        """ Make a variable for storage in the graph """
        return self.conf['rdf.namespace']["variable#"+var_name]

    def id_is_variable(self):
        """ Is the uriref a graph variable? """
        return DataObject._is_variable(self.identifier(query=True))

    @classmethod
    def _is_variable(cls,uri):
        """ Is the uriref a graph variable? """
        # We should be able to extract the type from the identifier
        if not isinstance(uri,R.URIRef):
            return False
        cn = cls._extract_class_name(uri)
        #print 'cn = ', cn
        return (cn == 'variable')

    @classmethod
    def _graph_variable_to_var(cls,uri):

        from urlparse import urlparse
        u = urlparse(uri)
        x = u.path.split('/')
        #print uri
        if x[2] == 'variable':
            #print 'fragment = ', u.fragment
            return R.Variable(u.fragment)
        else:
            return uri

    @classmethod
    def _graph_variable_to_var0(cls,uri):

        from urlparse import urlparse
        u = urlparse(uri)
        x = u.path.split('/')
        #print uri
        if x[2] == 'variable':
            #print 'fragment = ', u.fragment
            return "?"+u.fragment

    def identifier(self,query=False):
        """
        The identifier for this object in the rdf graph.

        This identifier may be randomly generated, but an identifier returned from the
        graph can be used to retrieve the specific object that it refers to.
        """
        if query and not self._id_is_set:
            return self._id_variable
        else:
            return self._id

    def make_identifier(self, data):
        import hashlib
        return R.URIRef(self.rdf_namespace["a"+hashlib.md5(str(data)).hexdigest()])

    def triples(self, query=False, visited_list=False, **kwargs):
        """
        Should be overridden by derived classes to return appropriate triples

        Returns
        --------
        An iterable of triples
        """
        if visited_list == False:
            visited_list = set()

        if self in visited_list:
            return
        else:
            visited_list.add(self)

        ident = self.identifier(query=query)
        yield (ident, R.RDF['type'], self.rdf_type)

        # For objects that are defined by triples, we can just release these.
        # However, they are still data objects, so they must have the above
        # triples released as well.
        for x in self._triples:
            yield x

        # Properties (of type Property) can be attached to an object
        # However, we won't require that there even is a property list in this
        # case.
        if hasattr(self, 'properties'):
            for x in self.properties:
                if isinstance(x, SimpleProperty):
                    if x.hasValue():
                        yield (ident, x.link, x.identifier(query=query))
                        for y in x.triples(query=query, visited_list=visited_list, **kwargs):
                            yield y
                    elif x.hasVariable():
                        yield (ident, x.link, x.identifier(query=query))
                        for y in x.triples(query=query, visited_list=visited_list, **kwargs):
                            yield y
                else:
                    for y in x.triples(query=query, visited_list=visited_list, **kwargs):
                        yield y

    def graph_pattern(self,query=False):
        """ Get the graph pattern for this object.

        It should be as simple as converting the result of triples() into a BGP
        """
        visited_list = set()
        return _triples_to_bgp(self.triples(query=query, visited_list=visited_list))

    def save(self):
        """ Write in-memory data to the database. Derived classes should call this to update the store. """

        ss = set()
        self.add_statements(self.triples(visited_list=ss, saving=True))

    def object_from_id(self,identifier,rdf_type=False):
        """ Load an object from the database using its type and id

        Parameters
        ----------
        identifier : rdflib.term.URIRef
            the object's id
        rdf_type : rdflib.term.URIRef
            the object's type. Optional.
        """
        if rdf_type:
            uri = rdf_type
        else:
            uri = identifier

        cn = self._extract_class_name(uri)
        o = DataObjectTypes[cn](ident=identifier)
        return o

    @classmethod
    def _extract_class_name(self,uri):
        from urlparse import urlparse
        u = urlparse(uri)
        x = u.path.split('/')
        if len(x) >= 3 and x[1] == 'entities':
            return x[2]

    @classmethod
    def _extract_property_name(self,uri):
        from urlparse import urlparse
        u = urlparse(uri)
        x = u.path.split('/')
        if len(x) >= 4 and x[1] == 'entities':
            return x[3]

    # Must resolve, somehow, to a set of triples that we can manipulate
    # For instance, one or more construct query could represent the object or
    # the triples might be stored in memory.
    @classmethod
    def DatatypeProperty(cls,*args,**kwargs):
        """ Create a SimpleProperty that has a simple type (string,number,etc) as its value

        Parameters
        ----------
        linkName : string
            The name of this Property.
        owner : PyOpenWorm.dataObject.DataObject
            The name of this Property.
        """
        return cls._create_property(*args,property_type='DatatypeProperty',**kwargs)

    @classmethod
    def ObjectProperty(cls, *args,**kwargs):
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
        return cls._create_property(*args,property_type='ObjectProperty',**kwargs)

    @classmethod
    def _create_property(cls, linkName, owner, property_type, value_type=False, multiple=False):
        assert(False)
        #XXX This should actually get called for all of the properties when their owner
        #    classes are defined.
        #    The initialization, however, must happen with the owner object's creation
        owner_class = cls
        owner_class_name = owner_class.__name__
        property_class_name = owner_class_name + "_" + linkName
        if value_type == False:
            value_type = DataObject

        c = None
        if property_class_name in DataObjectTypes:
            c = DataObjectTypes[property_class_name]
        else:
            if property_type == 'ObjectProperty':
                value_rdf_type = value_type.rdf_type
            else:
                value_rdf_type = False
            c = type(property_class_name,(SimpleProperty,),dict(linkName=linkName, property_type=property_type, value_rdf_type=value_rdf_type, owner_type=owner_class, multiple=multiple))
            DataObjectTypes[property_class_name] = c
            c.register()

        return c(owner=owner)

    @classmethod
    def register(cls):
        """ Registers the class as a DataObject to be included in the configured rdf graph.
            Puts this class under the control of the database for metadata.

        :return: None
        """
        # NOTE: This expects that configuration has been read in and that the database is available
        assert(issubclass(cls, DataObject))
        DataObjectTypes[cls.__name__] = cls
        _DataObjectsParents[cls.__name__] = [x for x in cls.__bases__ if issubclass(x, DataObject)]
        cls.parents = _DataObjectsParents[cls.__name__]
        cls.rdf_type = cls.conf['rdf.namespace'][cls.__name__]
        RDFTypeTable[cls.rdf_type] = cls
        cls.rdf_namespace = R.Namespace(cls.rdf_type + "/")
        cls.conf['rdf.namespace_manager'].bind(cls.__name__, cls.rdf_namespace)

    def load(self):
        """ Load in data from the database. Derived classes should override this for their own data structures.

        ``load()`` returns an iterable object which yields DataObjects which have the same class as the object and have, for the Properties set, the same values

        :param self: An object which limits the set of objects which can be returned. Should have the configuration necessary to do the query
        """
        if not DataObject._is_variable(self.identifier(query=True)):
            yield self
        else:
            trips = list(self.triples(query=True))
            type_trip_check = lambda t: ((t[1] == R.RDF['type']) and (isinstance(t[0], R.Variable) or DataObject._is_variable(t[0])))
            non_type_trips = [t for t in trips if not type_trip_check(t)]
            type_trips = [t for t in trips if type_trip_check(t)]

            if len(non_type_trips) == 0:
                gp = _triples_to_bgp(type_trips)
            else:
                gp = _triples_to_bgp(non_type_trips)
                if type_trips:
                    gp = gp + " . FILTER (EXISTS { "+_triples_to_bgp(type_trips)+" })"


            ident = self.identifier(query=True)
            ident = self._graph_variable_to_var(ident) # XXX: Assuming that this object doesn't have a set identifier
            q = "SELECT DISTINCT {0} {0}_type where {{ {{ {1} }} . {0} rdf:type {0}_type }} ORDER BY {0}".format(ident.n3(), gp)
            qres = self.rdf.query(q)
            results = _QueryResultsTypeResolver(self, qres)()
            for x in results:
                yield x

    def retract(self):
        """ Remove this object from the data store. """
        self.retract_statements(self.graph_pattern(query=True))

    def __getitem__(self, x):
        try:
            return DataUser.__getitem__(self, x)
        except KeyError:
            raise Exception("You attempted to get the value `%s' from `%s'. It isn't here. Perhaps you misspelled the name of a Property?" % (x, self))

    def getOwners(self, property_name):
        """ Return the owners along a property pointing to this object """
        from PyOpenWorm.v0.simpleProperty import SimpleProperty
        res = []
        for x in self.owner_properties:
            if isinstance(x, SimpleProperty):
                if str(x.linkName) == str(property_name):
                    res.append(x.owner)
        return res

class _QueryResultsTypeResolver(object):
    # Takes an iterable of (identifier, type) results in qres, sorted by the identifier
    # and adds the objects corresponding to the result list
    def __init__(self, ob, qres):
        self.ob = ob # The DataObject that created this QRTR
        self.qres = iter(qres) # The query results
        self.results = []

    def s(self):
        try:
            k = next(self.qres)
        except StopIteration:
            k = (None, None)
        return k

    def g0(self, ident, types):
        while ident is not None:
            k = self.s()
            n_ident = k[0]
            n_type = k[1]

            if n_ident != ident:
                o = self.ob.object_from_id(ident, get_most_specific_rdf_type(types))
                self.results.append(o)
                types = [n_type]
            else:
                types = [n_type] + types
            ident = n_ident

    def g(self):
        k = self.s()
        if k[0] is None:
            return
        else:
            self.g0(k[0], [k[1]])
    def __call__(self):
        self.g()
        return self.results

def get_most_specific_rdf_type(types):
    """ Gets the most specific rdf_type.

    Returns the URI corresponding to the lowest in the DataObject class hierarchy
    from among the given URIs.
    """
    most_specific_type = DataObject
    for x in types:
        cn = DataObject._extract_class_name(x) # TODO: Make a table to lookup by the class URI
        try:
            class_object = DataObjectTypes[cn]
            if issubclass(class_object, most_specific_type):
                most_specific_type = class_object
        except KeyError:
            L.warn("""A a Python class named "{}" corresponding to the type URI "{}" couldn't be found.
            You may want to import the module containing the class as well as add additional type
            annotations in order to resolve your objects to a more precise type than DataObject.""".format(cn, x))
    return most_specific_type.rdf_type


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
    def __init__(self,group_name,**kwargs):
        DataObject.__init__(self,**kwargs)
        self.add = values.ObjectProperty('value', owner=self)
        self.group_name = values.DatatypeProperty('name', owner=self)
        self.name(group_name)

    def identifier(self, query=False):
        return self.make_identifier(self.group_name)
