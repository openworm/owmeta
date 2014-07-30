import rdflib as R
from PyOpenWorm import DataUser
import traceback
import logging as L

__all__ = [ "DataObject", "DatatypeProperty", "ObjectProperty", "Property", "SimpleProperty", "_DataObjectsParents", "values"]

class X():
   pass

# in general it should be possible to recover the entire object from its identifier: the object should be representable as a connected graph.
# However, this need not be a connected *RDF* graph. Indeed, graph literals may hold information which can yield triples which are not
# connected by an actual node

def _bnode_to_var(x):
    return "?" + x

def _rdf_literal_to_gp(x):
    if isinstance(x,R.BNode):
        return _bnode_to_var(x)
    elif isinstance(x,R.URIRef) and DataObject._is_variable(x):
        return DataObject._graph_variable_to_var(x)
    else:
        return x.n3()

def _triples_to_bgp(trips):
    # XXX: Collisions could result between the variable names of different objects
    g = " .\n".join(" ".join(_rdf_literal_to_gp(x) for x in y) for y in trips)
    return g

_DataObjects = dict()
# TODO: Put the subclass relationships in the database
_DataObjectsParents = dict()

# We keep a little tree of properties in here
class DataObject(DataUser):
    """ An object backed by the database

    Attributes
    -----------
    rdf_type : rdflib.term.URIRef
        The RDF type URI for objects of this type
    rdf_namespace : rdflib.namespace.Namespace
        The rdflib namespace (prefix for URIs) for objects from this class
    properties : list of Property
        Properties

    """
    # Must resolve, somehow, to a set of triples that we can manipulate
    # For instance, one or more construct query could represent the object or
    # the triples might be stored in memory.

    @classmethod
    def register(cls):
        assert(issubclass(cls, DataObject))
        _DataObjects[cls.__name__] = cls
        _DataObjectsParents[cls.__name__] = [x for x in cls.__bases__ if issubclass(x, DataObject)]
        cls.parents = _DataObjectsParents[cls.__name__]

    def __init__(self,ident=False,triples=[],**kwargs):
        DataUser.__init__(self,**kwargs)
        self._triples = triples
        self._is_releasing_triples = False
        self.properties = []
        self.rdf_type = self.conf['rdf.namespace'][self.__class__.__name__]
        self.rdf_namespace = R.Namespace(self.rdf_type + "/")

        self._id_is_set = False

        if ident:
            self._id = R.URIRef(ident)
            self._id_is_set = True
        else:
            # Randomly generate an identifier if the derived class can't
            # come up with one from the start. Ensures we always have something
            # that functions as an identifier
            import random
            import struct
            v = struct.pack("=2f",random.random(),random.random())
            self._id_variable = self._graph_variable(self.__class__.__name__ + v.encode('hex'))
            self._id = self.make_identifier(v)

    def __eq__(self,other):
        return isinstance(other,DataObject) and (self.identifier() == other.identifier())

    def __str__(self):
        s = self.__class__.__name__ + "("
        s +=  ", ".join(str(x) for x in self.properties)
        s += ")"
        return s
    def __repr__(self):
        return self.__str__()

    def _graph_variable(self,var_name):
        """ Make a variable for storage the graph """
        return self.conf['rdf.namespace']["variable#"+var_name]

    @classmethod
    def _is_variable(self,uri):
        """ Is the uriref a graph variable? """
        # We should be able to extract the type from the identifier
        if not isinstance(uri,R.URIRef):
            return False
        cn = self._extract_class_name(uri)
        #print 'cn = ', cn
        return (cn == 'variable')

    @classmethod
    def _graph_variable_to_var(self,uri):
        from urlparse import urlparse
        u = urlparse(uri)
        x = u.path.split('/')
        #print uri
        if x[2] == 'variable':
            #print 'fragment = ', u.fragment
            return "?"+u.fragment

    def identifier(self,query=False):
        """
        The identifier for this object in the rdf graph
        This identifier is usually randomly generated, but an identifier returned from the
        graph can be used to retrieve the object.
        """
        if query and not self._id_is_set:
            return self._id_variable
        else:
            return self._id

    def make_identifier(self, data):
        import hashlib
        return R.URIRef(self.rdf_namespace[hashlib.sha224(str(data)).hexdigest()])

    def triples(self, query=False):
        """ Should be overridden by derived classes to return appropriate triples

        Returns
        --------
        An iterable of triples
        """
        # The default implementation, gives the object no representation or the one
        # explicitly given in __init__
        if not self._is_releasing_triples:
            # Note: We are _definitely_ assuming synchronous operation here.
            #       Anyway, this code should be idempotent, so that there's no need to lock it...
            self._is_releasing_triples = True
            ident = self.identifier(query=query)

            if not query:
                bases = self.parents
                while len(bases) > 0:
                    next_bases = set([])
                    for x in bases:
                        t = x(conf=self.conf).rdf_type
                        yield (ident, R.RDF['type'], t)
                        next_bases = next_bases | set(x.parents)
                    bases = next_bases

            yield (ident, R.RDF['type'], self.rdf_type)

            # For objects that are defined by triples, we can just release these.
            # However, they are still data objects, so they must have the above
            # triples released as well.
            for x in self._triples:
                yield x

            # Properties (of type Property) can be attached to an object
            # However, we won't require that there even is a property list in this
            # case.
            try:
                for x in self.properties:
                    for y in x.triples(query=query):
                        yield y
            except AttributeError:
                # XXX Is there a way to check what the failed attribute reference was?
                pass

            self._is_releasing_triples = False

    def graph_pattern(self,query=False):
        """ Get the graph pattern for this object.

        It should be as simple as converting the result of triples() into a BGP

        By default conversion from triples() will treat BNodes as variables
        """
        return _triples_to_bgp(self.triples(query=query))

    def save(self):
        """ Write in-memory data to the database. Derived classes should call this to update the store. """

        self.add_statements(self._skolemize_triples(self.triples()))

    def _skolemize_triples(self, trips):
        # Turn all of the BNodes into concrete_identifiers
        for t in trips:
            new_t = []
            for z in t:
                if isinstance(z,R.BNode):
                    z = self.make_identifier(z)
                new_t.append(z)
            yield new_t

    def object_from_id(self,identifier,rdf_type=False):
        """ Load an object from the database using its type tag """
        # XXX: This is a class method because we need to get the conf
        # We should be able to extract the type from the identifier
        if rdf_type:
            uri = rdf_type
        else:
            uri = identifier

        cn = self._extract_class_name(uri)
        # if its our class name, then make our own object
        # if there's a part after that, that's the property name
        o = _DataObjects[cn](ident=identifier, conf=self.conf)
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


    def load(self):
        """ Load in data from the database. Derived classes should override this for their own data structures.

        :param self: An object which limits the set of objects which can be returned. Should have the configuration necessary to do the query
        """
        # 'loading' an object _always_ means doing a query. When we do the query, we identify all of the result sets that can make objects in the current
        # graph and convert them into objects of the type of the querying object.
        #
        gp = self.graph_pattern(query=True)
        # Append some extra patterns to get *all* values for *all* the properties
        #for prop in self.properties:
            ## hack, hack, hack
            #if isinstance(prop, SimpleProperty):
                #z = prop.v
                #prop.v = []
                #prop_gp = prop.graph_pattern(query=True)
                #gp += " .\n"+prop_gp
                #prop.v = z
        ident = self.identifier(query=True)
        varlist = [n.linkName for n in self.properties if isinstance(n, SimpleProperty) ]
        if DataObject._is_variable(ident):
            varlist.append(self._graph_variable_to_var(ident)[1:])
        # Do the query/queries
        q = "Select distinct "+ " ".join("?" + x for x in varlist)+"  where { "+ gp +".}"
        L.debug('load_query='+q)
        qres = self.conf['rdf.graph'].query(q)
        for g in qres:
            # attempt to get a value for each of the properties this object has
            # if there isn't a value for this property

            # XXX: Should distinguish datatype and object properties to set them up accordingly.

            # If our own identifier is a BNode, then the binding we get will be for a distinct object
            # otherwise, the object we get is really the same as this object

            if DataObject._is_variable(ident):
                new_ident = g[self._graph_variable_to_var(ident)[1:]]
            else:
                new_ident = ident

            new_object = self.object_from_id(new_ident)

            for prop in self.properties:
                if isinstance(prop, SimpleProperty):
                    # get the linkName
                    link_name = prop.linkName
                    # Check if the name is in the result
                    if g[link_name] is not None:
                        new_object_prop = getattr(new_object, link_name)
                        result_value = g[link_name]

                        if result_value is not None \
                                and not isinstance(result_value, R.BNode) \
                                and not DataObject._is_variable(result_value):
                            # XXX: Maybe should verify that it's an rdflib term?
                            # Create objects from the bound variables
                            if isinstance(result_value, R.Literal) \
                            and new_object_prop.property_type == 'DatatypeProperty':
                                new_object_prop(result_value)
                            elif new_object_prop.property_type == 'ObjectProperty':
                                new_object_prop(self.object_from_id(result_value, new_object_prop.value_rdf_type))
                    else:
                        our_value = getattr(self, link_name)
                        setattr(new_object, link_name, our_value)
            yield new_object

    def retract(self):
        """ Remove this object from the data store. """
        self.retract_statements(self.graph_pattern(query=True))

# Define a property by writing the get
class Property(DataObject):
    """ Store a value associated with a DataObject

    Properties can be be accessed like methods. A method call like::

        a.P()

    for a property ``P`` will return values appropriate to that property for ``a``,
    the `owner` of the property.

    Parameters
    ----------
    owner : PyOpenWorm.dataObject.DataObject
        The owner of this property
    name : string
        The name of this property. Can be accessed as an attribute like::

            owner.name

    """
    def __init__(self, name=False, owner=False, **kwargs):
        DataObject.__init__(self, **kwargs)
        self.owner = owner
        if self.owner:
            self.owner.properties.append(self)
            if name:
                setattr(self.owner, name, self)
            self.conf = self.owner.conf

        # XXX: Default implementation is a box for a value
        self._value = False

    def __getattr__(self, f):
        """ Executes the get() query for this object and creates a new generator
        pulling values from each result
        """
        return _PropertyLink(self.get(), f)

    def get(self,*args):
        """ Get the things which are on the other side of this property

        Derived classes must override.
        """
        # This should run a query or return a cached value
        raise NotImplementedError()
    def set(self,*args,**kwargs):
        """ Set the value of this property

        Derived classes must override.
        """
        # This should set some values and call DataObject.save()
        raise NotImplementedError()
    def __call__(self,*args,**kwargs):
        if len(args) > 0 or len(kwargs) > 0:
            self.set(*args,**kwargs)
            return self
        else:
            return self.get(*args,**kwargs)
    # Get the property (a relationship) itself
class _PropertyLink(Property):
    def __init__(self, gen, link):
        self._last = gen
        self._link = link
    def get(self):
        for i in self._last:
            for x in getattr(i, self._link).get():
                yield x

    def __getattr__(self, n):
        return self.__class__(self.get(), n)

class SimpleProperty(Property):
    """ A property that has just one link to a literal or DataObject """

    def __init__(self,**kwargs):
        if not hasattr(self,'linkName'):
            self.__class__.linkName=self.__class__.__name__ + "property"
        Property.__init__(self, name=self.linkName, **kwargs)
        self.v = []
        if (self.owner==False) and hasattr(self,'owner_type'):
            self.owner = self.owner_type(conf=self.conf)

        if self.owner!=False:
            self.link = self.owner.rdf_namespace[self.linkName]

    def get(self):
        if len(self.v) > 0:
            for x in self.v:
                yield x
        else:
            owner_id = self.owner.identifier(query=True)
            if DataObject._is_variable(owner_id):
                gp = self.owner.graph_pattern(query=True)
            else:
                gp = self.graph_pattern(query=True)

            var = "?"+self.linkName
            q = "select distinct " +  var + " where { " + gp + " }"
            L.debug("get query = " + q)
            qres = self.rdf.query(q)
            for x in qres:
                if self.property_type == 'DatatypeProperty' \
                        and not DataObject._is_variable(x[0]) \
                        and x[0] is not None:
                    yield str(x[0])
                elif self.property_type == 'ObjectProperty':
                    # XXX: We can pull the type from the graph. Just be sure
                    #   to get the most specific type
                    yield self.object_from_id(x[0], self.value_rdf_type)


    def set(self,v):
        import bisect
        bisect.insort(self.v,v)

    def triples(self,query=False):
        owner_id = self.owner.identifier(query=query)
        ident = self.identifier(query=query)
        value_property = self.conf['rdf.namespace']['SimpleProperty/value']


        if len(self.v) > 0:
            for x in Property.triples(self,query=query):
                yield x
            yield (owner_id, self.link, ident)
            for x in self.v:
                try:
                    if self.property_type == 'DatatypeProperty':
                        yield (ident, value_property, R.Literal(x))
                    elif self.property_type == 'ObjectProperty':
                        yield (ident, value_property, x.identifier(query=query))
                        for t in x.triples(query=query):
                            yield t
                except Exception:
                    traceback.print_exc()
        else:
            # XXX : Note: we insert 'variables' into the graph so that we don't
            # have to do OPTIONAL patterns in load.
            # We could instead use Triple objects to which we attach 'optional' tags
            # to indicate that the triple should be in an optional pattern when
            # queried.
            gv = self._graph_variable(self.linkName)
            yield (owner_id, self.link, ident)
            yield (ident, value_property, gv)

            # Removing
            #if self.property_type == 'ObjectProperty':
                ## The value
                #if not hasattr(self,'value_rdf_type'):
                    #yield (gv, R.RDF['type'], DataObject(conf=self.conf).rdf_type)
                #else:
                    #yield (gv, R.RDF['type'], self.value_rdf_type)
    def load(self):
        """ Load in data from the database. Derived classes should override this for their own data structures.

        :param self: An object which limits the set of objects which can be returned. Should have the configuration necessary to do the query

        """
        # This load is way simpler since we just need the values for this property
        gp = self.graph_pattern(query=True)
        q = "Select distinct ?"+self.linkName+"  where { "+ gp +" . }"
        L.debug('load_query='+q)
        qres = self.conf['rdf.graph'].query(q)
        for k in qres:
            k = k[0]
            value = False
            if not self._is_variable(k):
                if self.property_type == 'ObjectProperty':
                    value = self.object_from_id(k)
                elif self.property_type == 'DatatypeProperty':
                    value = str(k)

                if value:
                    self.v.append(value)
        yield self

    def identifier(self,query=False):
        """ Return the URI for this object

        Parameters
        ----------
        query: bool
            Indicates whether the identifier is to be used in a query or not
        """
        ident = DataObject.identifier(self,query=query)
        if self._id_is_set:
            return ident

        if query:
            # If we're querying then our identifier should be a variable if either our value is empty
            # or our owner's identifier is a variable
            owner_id = self.owner.identifier(query=query)
            vlen = len(self.v)
            #print vlen
            #print owner_id
            if vlen == 0 or DataObject._is_variable(owner_id):
                return ident
        # Intentional fall through from if statement ...
        value_data = ""
        if self.property_type == 'DatatypeProperty':
            value_data = "".join(str(x) for x in self.v)
        elif self.property_type == 'ObjectProperty':
            value_data = "".join(str(x.identifier()) for x in self.v)

        return self.make_identifier((self.owner.identifier(query=query), self.link, value_data))

    def __str__(self):
        return unicode(self.linkName + "=" + unicode(";".join(unicode(x) for x in self.v)))

def DatatypeProperty(*args,**kwargs):
    """ Create a SimpleProperty that has a simple type (string,number,etc) as its value

    Parameters
    ----------
    linkName : string
        The name of this Property.
    owner : PyOpenWorm.dataObject.DataObject
        The name of this Property.
    """
    return _create_property(*args,property_type='DatatypeProperty',**kwargs)

def ObjectProperty(*args,**kwargs):
    """ Create a SimpleProperty that has a complex DataObject as its value

    Parameters
    ----------
    linkName : string
        The name of this Property.
    owner : PyOpenWorm.dataObject.DataObject
        The name of this Property.
    value_type : type
        The type of DataObject fro values of this property
    """
    return _create_property(*args,property_type='ObjectProperty',**kwargs)

def _create_property(linkName, owner, property_type, value_type=DataObject):
    #XXX This should actually get called for all of the properties when their owner
    #    classes are defined.
    #    The initialization, however, must happen with the owner object's creation
    owner_class = owner.__class__
    owner_class_name = owner_class.__name__
    property_class_name = owner_class_name + "_" + linkName

    c = None
    if property_class_name in _DataObjects:
        c = _DataObjects[property_class_name]
    else:
        if property_type == 'ObjectProperty':
            value_rdf_type = value_type(conf=owner.conf).rdf_type
        else:
            value_rdf_type = False

        c = type(property_class_name,(SimpleProperty,),dict(linkName=linkName, property_type=property_type, value_rdf_type=value_rdf_type, owner_type=owner_class))
        _DataObjects[property_class_name] = c
        c.register()

    return c(owner=owner, conf=owner.conf)

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
        self.add = ObjectProperty('value', owner=self)
        DatatypeProperty('name', owner=self)
        self.name(group_name)
