import rdflib as R
from PyOpenWorm import DataUser
import PyOpenWorm

__all__ = [ "DataObject", "DatatypeProperty", "ObjectProperty", "Property", "SimpleProperty"]

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

class DataObject(DataUser):
    """ An object backed by the database """
    # Must resolve, somehow, to a set of triples that we can manipulate
    # For instance, one or more construct query could represent the object or
    # the triples might be stored in memory.

    def __init__(self,ident=False,triples=[],**kwargs):
        DataUser.__init__(self,**kwargs)

        self._triples = triples
        self._is_releasing_triples = False
        self.properties = []
        self.rdf_type = self.conf['rdf.namespace'][self.__class__.__name__]
        self.rdf_namespace = R.Namespace(self.rdf_type + "/")

        if ident:
            self._id = R.URIRef(ident)
        else:
            # Randomly generate an identifier if the derived class can't
            # come up with one from the start. Ensures we always have something
            # that functions as an identifier
            import random
            import struct
            v = struct.pack("=f",random.random()).encode("hex")
            self._id = R.BNode(self.__class__.__name__ + v)

    def __eq__(self,other):
        return (self.identifier() == other.identifier())

    def __str__(self,_level=0):
        s = (" " * _level) + self.__class__.__name__
        s += '\n'
        s +=  "\n".join((" " * (_level + 1))+str(x) for x in self.properties)
        return s

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

    def identifier(self):
        """
        The identifier for this object in the rdf graph
        This identifier is usually randomly generated, but an identifier returned from the
        graph can be used to retrieve the object.
        """
        return self._id

    def make_identifier(self, data):
        import hashlib
        return R.URIRef(self.rdf_namespace[hashlib.sha224(str(data)).hexdigest()])

    def triples(self):
        """ Should be overridden by derived classes to return appropriate triples
        :return: An iterable of triples
        """
        # The default implementation, gives the object no representation or the one
        # explicitly given in __init__
        if not self._is_releasing_triples:
            # Note: We are _definitely_ assuming synchronous operation here.
            #       Anyway, this code's idempotent. There's no need to lock it...
            self._is_releasing_triples = True
            yield (self.identifier(), R.RDF['type'], self.rdf_type)
            for x in self._triples:
                yield x
            for x in self.properties:
                for y in x.triples():
                    yield y
            self._is_releasing_triples = False

    def graph_pattern(self):
        """ Get the graph pattern for this object.
        It should be as simple as converting the result of triples() into a BGP
        By default conversion from triples() will treat BNodes as variables
        """
        return _triples_to_bgp(self.triples())

    def _n3(self):
        return u".\n".join( x[0].n3() + x[1].n3()  + x[2].n3() for x in self.triples())

    def n3(self):
        return self._n3()

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

    @classmethod
    def object_from_id(self,identifier,rdf_type=False):
        """ Load an object from the database using its type tag """
        # We should be able to extract the type from the identifier
        if rdf_type:
            cn = self._extract_class_name(rdf_type)
        else:
            cn = self._extract_class_name(identifier)
        if cn is not None:
            cls = getattr(PyOpenWorm,cn)
            b = cls()
            b.identifier = lambda : identifier
            return b

    @classmethod
    def _extract_class_name(self,uri):
        from urlparse import urlparse
        u = urlparse(uri)
        x = u.path.split('/')
        #print 'ecn, uri =', uri
        if x[1] == 'entities':
            return x[2]

    def load(self):
        """ Load in data from the database. Derived classes should override this for their own data structures.
        :param self: An object which limits the set of objects which can be returned. Should have the configuration necessary to do the query
        """
        # 'loading' an object _always_ means doing a query. When we do the query, we identify all of the result sets that can make objects in the current
        # graph and convert them into objects of the type of the querying object.
        #
        import logging as L
        gp = self.graph_pattern()
        L.debug('loading...')
        # Append some extra patterns to get all values for the properties
        for prop in self.properties:
            # hack, hack, hack
            if isinstance(prop, SimpleProperty):
                z = prop.v
                prop.v = []
                prop_gp = prop.graph_pattern()
                gp += " .\n"+prop_gp
                prop.v = z
        ident = self.identifier()
        varlist = [n.linkName for n in self.properties if isinstance(n, SimpleProperty) ]
        if isinstance(ident,R.BNode):
            varlist.append(ident)
        # Do the query/queries
        q = "Select distinct "+ " ".join("?" + x + " ?typeof_" + x for x in varlist)+"  where { "+ gp +"\n"+ " .\n".join("OPTIONAL { ?" + x + " rdf:type ?typeof_" + x + " }" for x in varlist) + " }"
        L.debug('load query = ' + q)
        qres = self.conf['rdf.graph'].query(q)
        L.debug('returned from query')
        for g in qres:
            L.debug('got result = ' + str(g))
            # attempt to get a value for each of the properties this object has
            # if there isn't a value for this property

            # XXX: Should distinguish datatype and object properties to set them up accordingly.

            # If our own identifier is a BNode, then the binding we get will be for a distinct object
            # otherwise, the object we get is really the same as this object

            if isinstance(ident,R.BNode):
                new_ident = g[str(ident)]
            else:
                new_ident = ident

            new_object = self.__class__()

            for prop in self.properties:
                if isinstance(prop, SimpleProperty):
                    # get the linkName
                    link_name = prop.linkName
                    # Check if the name is in the result
                    if g[link_name] is not None:
                        new_object_prop = getattr(new_object, link_name)
                        result_value = g[link_name]
                        result_type = False
                        if g['typeof_'+link_name] is not None:
                            result_type = g['typeof_'+link_name]

                        if result_value is not None \
                                and not isinstance(result_value, R.BNode) \
                                and not DataObject._is_variable(result_value):
                            # XXX: Maybe should verify that it's an rdflib term?
                            # Create objects from the bound variables
                            if isinstance(result_value, R.Literal) and isinstance(new_object_prop, DatatypeProperty):
                                new_object_prop(result_value)
                            elif isinstance(new_object_prop, ObjectProperty):
                                new_object_prop(DataObject.object_from_id(result_value, result_type))
                    else:
                        our_value = getattr(self, link_name)
                        setattr(new_object, link_name, our_value)
            yield new_object

    def retract(self):
        """ Remove this object from the data store. """
        import logging as L
        for x in self.triples():
            ll = L.getLogger().getEffectiveLevel()
            if ll == L.DEBUG:
                L.debug("got a bnode in retract = " + str(x))
        self.retract_statements(_triples_to_bgp(self.triples()))

    def uploader(self):
        """ Get the uploader for this relationship """
        uploader_n3_uri = self.conf['rdf.namespace']['uploader'].n3()
        q = """
        Select ?u where
        {
        GRAPH ?g {
        """+self._n3()+"""}

        ?g """+uploader_n3_uri+""" ?u.
        } LIMIT 1
        """
        qres = self.conf['rdf.graph'].query(q)
        uploader = None
        for x in qres:
            uploader = x['u']
            break
        return str(uploader)

    def upload_date(self):
        """ Get the date of upload for this relationship
        :return: the date(s) of upload for this object
        """
        upload_date_n3_uri = self.conf['rdf.namespace']['upload_date'].n3()
        q = """
        Select ?u where
        {
        GRAPH ?g {
        """+self._n3()+"""}

        ?g """+upload_date_n3_uri+""" ?u.
        } LIMIT 1
        """
        qres = self.conf['rdf.graph'].query(q)
        ud = None
        for x in qres:
            ud = x['u']
            break

        return str(ud)

# Define a property by writing the get
class Property(DataObject):
    def __init__(self, owner, **kwargs):
        """ Initialize with the owner of this property.
        The owner has a distinct role in each subclass of Property
        """
        DataObject.__init__(self, **kwargs)
        self.owner = owner
        self.owner.properties.append(self)
        self.conf = self.owner.conf

        # XXX: Default implementation is a box for a value
        self._value = False

    def get(self,*args):
        """ Get the things which are on the other side of this property """
        # This should run a query or return a cached value
        raise NotImplementedError()
    def set(self,*args,**kwargs):
        """ Set the value of this property """
        # This should set some values and call DataObject.save()
        raise NotImplementedError()
    def __call__(self,*args,**kwargs):
        if len(args) > 0 or len(kwargs) > 0:
            self.set(*args,**kwargs)
            return self
        else:
            return self.get(*args,**kwargs)
    # Get the property (a relationship) itself
class SimpleProperty(Property):
    """ A property that has just one link to a literal or DataObject """

    def __init__(self,linkName,**kwargs):
        Property.__init__(self,**kwargs)
        self.v = []
        self.link = self.owner.rdf_namespace[linkName]
        self.linkName = linkName
        setattr(self.owner,linkName, self)

    def get(self):
        if self.v:
            return self.v
        else:
            gp = self.owner.graph_pattern()
            var = "?"+self.linkName
            qres = self.rdf.query("select distinct " +  var + " where { " + gp + " }")
            r = [str(x[0]) for x in qres if not isinstance(x[0],R.BNode)]
            return r

    def set(self,v):
        self.v.append(v)

    def triples(self):
        owner_id = self.owner.identifier()
        ident = self.identifier()
        yield (ident, R.RDF['type'], self.link)
        yield (owner_id, self.link, ident)
        if len(self.v) > 0:
            for x in self.v:
                if isinstance(self, DatatypeProperty):
                    yield (ident, self.rdf_namespace['value'], R.Literal(x))
                elif isinstance(self, ObjectProperty):
                    yield (ident, self.rdf_namespace['value'], x.identifier())
        else:
            yield (ident, self.rdf_namespace['value'], self._graph_variable(self.linkName))

    def __str__(self):
        return str(self.linkName + "=" + str(self.v))

class ObjectProperty(SimpleProperty):
    pass

class DatatypeProperty(SimpleProperty):
    pass
