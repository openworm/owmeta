import rdflib as R
from PyOpenWorm import DataUser
import PyOpenWorm

class X():
   pass

# in general it should be possible to recover the entire object from its identifier: the object should be representable as a connected graph.
# However, this need not be a connected *RDF* graph. Indeed, graph literals may hold information which can yield triples which are not
# connected by an actual node
def _bnode_to_var(x):
    return "?" + x

def _rdf_literal_to_n3(x):
    if isinstance(x,R.BNode):
        return _bnode_to_var(x)
    else:
        return x.n3()

def _triples_to_bgp(trips):
    g = "\n".join(" ".join(_rdf_literal_to_n3(x) for x in y) for y in trips)
    return g

class DataObject(DataUser):
    """ An object backed by the database """
    # Must resolve, somehow, to a set of triples that we can manipulate
    # For instance, one or more construct query could represent the object or
    # the triples might be stored in memory.

    def __init__(self,ident=False,triples=[],conf=False):
        DataUser.__init__(self,conf=conf)
        if ident:
            self._id = ident
        else:
            # Randomly generate an identifier if the derived class can't
            # come up with one from the start. Ensures we always have something
            # that functions as an identifier
            import random
            import struct
            v = struct.pack("=f",random.random()).encode("hex")
            self._id = BNode(self.__class__.__name__ + v)

        self._triples = triples
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
        return R.URIRef(self._id)

    def make_identifier(self, data):
        import hashlib
        return R.URIRef(self.rdf_namespace[hashlib.sha224(str(data)).hexdigest()])

    def triples(self):
        """ Should be overridden by derived classes to return appropriate triples
        :return: An iterable of triples
        """
        # The default implementation, gives the object no representation or the one
        # explicitly given in __init__
        for x in self._triples:
            yield x

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
    def query_pattern(self):
        """ Return the pattern, variables to extract, and bindings for other variables in order to load this object from the graph
        :return (pattern_string, variables, bindings):
        """
        raise NotImplementedError()

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
    def __init__(self, owner, conf=False):
        """ Initialize with the owner of this property.
        The owner has a distinct role in each subclass of Property
        """
        DataObject.__init__(self, owner, conf=conf)
        self.owner = owner
        if not hasattr(self.owner,'properties'):
            self.owner.properties = [self]
        else:
            self.owner.properties.append(self)

        # XXX: Assuming that nothing else will come in and reset
        # triples() without preserving this one!
        if not hasattr(self.owner,'triples'):
            self.owner.triples = self.triples
        else:
            def more_triples():
                for x in self.owner.triples():
                    yield x
                for x in self.triples():
                    yield x
            self.owner.triples = more_triples()

        # XXX: Default implementation is a box for a value
        self._value = False

    def get(self):
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
            self.save()
            return self
        else:
            return self.get()
    # Get the property (a relationship) itself
class SimpleProperty(Property):
    """ A property that has just one link to a literal value """

    def __init__(self,owner,linkName,conf=False):
        if conf == False:
            conf = owner.conf
        Property.__init__(self,owner,conf=conf)
        self.v = False
        self.link = owner.rdf_namespace[linkName]
        self.linkname = linkName

    def get(self):
        if self.v:
            return self.v
        else:
            query = "Select ?x where { %s %s ?x } " % (self.owner.identifier().n3(), self.link.n3())
            qres = self.rdf.query(query)
            return [str(x['x']) for x in qres]

    def set(self,v):
        if hasattr(v,'__iter__'):
            self.v = v
        else:
            self.v = [v]
    def query_pattern(self):
        q = """{ ?p %s ?v
                 ; %s ?l }
            """ % (self.rdf_namespace['value'], self.rdf_namespace['type'])
        variables = ("v",)
        bindings = {"l":self.linkname}
        return (q,variables,bindings)

    def identifier(self):
        return self.make_identifier((self.linkname,self.v))

    def triples(self):
        owner_id = self.owner.identifier()
        ident = self.identifier()
        try:
            for x in self.v:
                yield (ident, self.rdf_namespace['owner'], owner_id)
                yield (owner_id, self.rdf_namespace['value'], R.Literal(x))
                yield (owner_id, R.RDF['type'], self.linkName)
        except:
            if self.v:
                yield (owner_id, self.link, R.Literal(self.v))

