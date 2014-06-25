import rdflib as R
from PyOpenWorm import DataUser, Configure

class DataObject(DataUser):
    """ An object backed by the database """
    # Must resolve, somehow, to a set of triples that we can manipulate
    # For instance, one or more construct query could represent the object or
    # the triples might be stored in memory.
    def __init__(self,ident="",triples=[],conf=False):
        DataUser.__init__(self,conf=conf)
        self._id = ident
        self._triples = triples

    def identifier(self):
        """
        The identifier for this object in the rdf graph
        This identifier should be based on identifying characteristics of the object
        """
        return R.URIRef(self._id)

    def triples(self):
        """ Should be overridden by derived classes to return appropriate triples
        :return: An iterable of triples
        """
        for x in self._triples:
            yield x

    def _n3(self):
        return ".\n".join( " ".join(y.n3() for y in x) for x in self.triples())

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
