import rdflib as R
from PyOpenWorm import DataUser, Configure

class X():
   pass

class IDError(BaseException):
    def __init__(self, s):
        BaseException.__init__(self,"No identifier for %s"%str(s))
# in general it should be possible to recover the entire object from its identifier: the object should be representable as a connected graph.
# However, this need not be a connected *RDF* graph. Indeed, graph literals may hold information which can yield triples which are not
# connected by an actual node

class DataObject(DataUser):
    """ An object backed by the database """
    # Must resolve, somehow, to a set of triples that we can manipulate
    # For instance, one or more construct query could represent the object or
    # the triples might be stored in memory.
    def __init__(self,ident=False,triples=[],conf=False):
        DataUser.__init__(self,conf=conf)
        self._id = ident
        self._triples = triples
        self.rdf_type = self.conf['rdf.namespace'][self.__class__.__name__]
        self.rdf_namespace = R.Namespace(self.rdf_type + "/")

    def identifier(self):
        """
        The identifier for this object in the rdf graph
        This identifier should be based on identifying characteristics of the object
        Only one identifier can be returned. If more than one could be returned based
        on the object's characteristics, one in returned randomly!
        """
        if not self._id:
            raise IDError(self)
        return R.URIRef(self._id)

    def triples(self):
        """ Should be overridden by derived classes to return appropriate triples
        :return: An iterable of triples
        """
        for x in self._triples:
            yield x

    def _n3(self):
        return u".\n".join( x[0].n3() + x[1].n3()  + x[2].n3() for x in self.triples())

    def n3(self):
        return self._n3()

    def save(self):
        """ Write in-memory data to the database. Derived classes should call this to update the store. """
        self.add_statements(self.triples())

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
            return self
        else:
            return self.get()
    # Get the property (a relationship) itself
class SimpleProperty(Property):
    """ A property that has just one link to a literal value """

    def __init__(self,owner,linkName,conf=False):
        if conf==False:
            conf = owner.conf
        Property.__init__(self,owner,conf=conf)
        self.v = False
        self.link = owner.rdf_namespace[linkName]

    def get(self):
        if self.v:
            return self.v
        else:
            qres = self.rdf.query("Select ?x where { %s %s ?x } " % (self.owner.identifier().n3(), self.link.n3()))
            return [str(x['x']) for x in qres]

    def set(self,v):
        if hasattr(v,'__iter__'):
            self.v = v
        else:
            self.v = [v]

    def identifier(self):
        return self.conf['molecule_name'](self.v)

    def triples(self):
        owner_id = self.owner.identifier()
        try:
            for x in self.v:
                yield (owner_id, self.link, R.Literal(x))
        except:
            if self.v:
                yield (owner_id, self.link, R.Literal(self.v))

