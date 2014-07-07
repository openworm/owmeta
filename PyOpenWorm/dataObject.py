import rdflib as R
from PyOpenWorm import DataUser
import PyOpenWorm

__all__ = [ "DataObject", "DatatypeProperty", "ObjectProperty", "Property"]

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
        if ident:
            self._id = ident
        else:
            # Randomly generate an identifier if the derived class can't
            # come up with one from the start. Ensures we always have something
            # that functions as an identifier
            import random
            import struct
            v = struct.pack("=f",random.random()).encode("hex")
            self._id = R.BNode(self.__class__.__name__ + v)

        self._triples = triples
        self._is_releasing_triples = False
        self.properties = []
        self.rdf_type = self.conf['rdf.namespace'][self.__class__.__name__]
        self.rdf_namespace = R.Namespace(self.rdf_type + "/")
    def __eq__(self,other):
        return (self.identifier() == other.identifier())
    def identifier(self):
        """
        The identifier for this object in the rdf graph
        This identifier should be based on identifying characteristics of the object.
        Only one identifier can be returned. If more than one could be returned based
        on the object's characteristics, one is returned randomly!
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
            #       Anyway, this codes idempotent. There's no need to lock it...
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
        self.add_statements(self.triples())

    @classmethod
    def object_from_id(self,identifier,rdf_type=False):
        """ Load an object from the database using its type tag """
        # We should be able to extract the type from the identifier
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
        if x[1] == 'entities':
            return x[2]

    def load(self):
        """ Load in data from the database. Derived classes should override this for their own data structures.
        :param self: An object which limits the set of objects which can be returned. Should have the configuration necessary to do the query
        """
        # 'loading' an object _always_ means doing a query. When we do the query, we identify all of the result sets that can make objects in the current
        # graph and convert them into objects of the type of the querying object.
        #
        # Steps:
        # - Do the query/queries
        # - Create objects from the bound variables
        gp = self.graph_pattern()
        varlist = [n.linkName for n in self.properties if isinstance(n, SimpleProperty) ]
        qres = self.conf['rdf.graph'].query("Select distinct "+ " ".join("?" + x for x in varlist)+"  where { "+ gp +" }")
        for g in qres:
            # attempt to get a value for each of the properties this object has
            # if there isn't a value for this property

            # XXX: Should distinguish datatype and object properties to set them up accordingly.
            # Assuming any uri is an identifier :(
            new_object = self.__class__()
            for prop in self.properties:
                if isinstance(prop, SimpleProperty):
                    # get the linkName
                    link_name = prop.linkName
                    # Check if the name is in the result
                    if link_name in g:
                        new_object_prop = getattr(new_object, link_name)
                        if isinstance(new_object_prop, DatatypeProperty):
                            new_object_prop(qres[link_name])
                        elif isinstance(new_object_prop, DatatypeProperty):
                            new_object_prop(DataObject.object_from_id(ident=qres[link_name]))
                    else:
                        our_value = getattr(self, link_name)
                        setattr(new_object, link_name, our_value)
            yield new_object

    def retract(self):
        """ Remove this object from the data store. """
        self.remove_statements(self._n3())

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
        if hasattr(v,'__iter__'):
            self.v = v
        else:
            self.v = [v]

    def triples(self):
        owner_id = self.owner.identifier()
        ident = self.identifier()
        yield (ident, self.rdf_namespace['owner'], owner_id)
        yield (ident, R.RDF['type'], self.link)
        if len(self.v) > 0:
            for x in self.v:
                if isinstance(self, DatatypeProperty):
                    yield (ident, self.rdf_namespace['value'], R.Literal(x))
                elif isinstance(self, ObjectProperty):
                    yield (ident, self.rdf_namespace['value'], x.identifier())
                    for z in x.triples():
                        yield z
        else:
            yield (ident, self.rdf_namespace['value'], R.BNode(self.linkName))

    def __str__(self):
        return str(self.linkName + "=" + str(self.v))

class ObjectProperty(SimpleProperty):
    pass

class DatatypeProperty(SimpleProperty):
    pass
