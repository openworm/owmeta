"""
Created on Sun Feb 23 17:10:53 2014

@author: slarson
@author: mwatts15

An Evidence object represents a single document

"""
from PyOpenWorm import DataObject, Configure, Relationship
import rdflib as R

class EvidenceError(BaseException):
    pass

class Evidence(DataObject):
    def __init__(self, conf=False, **source):
        # Get the type of the evidence (a paper, a lab, a uri)
        # We keep track of a set of fields for the evidence.
        # Some of the fields are pulled from provided URIs and
        # some is provided by the user.
        #
        # Turns into a star graph
        #
        # Evidence field1 value1
        #        ; field2 value2
        #        ; field3 value3 .
        DataObject.__init__(self, conf)
        self._fields = dict()
        self.namespace = R.Namespace(self.conf['rdf.namespace']['Evidence'] + '/')
        for k in source:
            if k in ('pubmed', 'pmid'):
                self._fields['pmid'] = source[k]
                break
            if k in ('wormbase', 'wbid'):
                self._fields['wormbase'] = source[k]
                self._wormbase_extract()
                break
            if k in ('bibtex'):
                self._fields['bibtex'] = source[k]
                break
            if k in ('person'):
                self._fields['person'] = source[k]
                break

    def add_data(self, k, v):
        """ Add a field

            :param k: Field name
            :param v: Field value
        """
        # Confirm that pmid contains a valid pubmed id
        self._fields[k] = v

    def asserts(self,stmt=False):
        """
        State that this Evidence asserts that the relationship is true.

        Example::

            import bibtex
            bt = bibtex.parse("my.bib")
            n1 = Neuron("AVAL")
            n2 = Neuron("DA3")
            c = Connection(pre=n1,post=n2,class="synapse")
            e = Evidence(bibtex=bt['white86'])
            e.asserts(c)

        Other methods return objects which asserts accepts.

        Example::

            n1 = Neuron("AVAL")
            r = n1.neighbor("DA3")
            e = Evidence(bibtex=bt['white86'])
            e.asserts(r)
        """
        if stmt:
            assert(isinstance(stmt,Relationship))
            trips = stmt.n3()
            graph_uri = self.conf['molecule_name'](trips)
            update_stmt = "insert data { graph %s { %s } . %s %s %s }" % (graph_uri.n3(), trips, self.identifier().n3(), self.namespace['asserts'].n3(), graph_uri.n3())
            # insert the statement
            self.conf['rdf.graph'].update(update_stmt)
        else:
            # Query for the evidence asserted by this
            query_stmt = "select  ?s ?p ?o  where { graph ?g { ?s ?p ?o } . %s %s ?g }" % (self.identifier().n3(), self.namespace['asserts'].n3())
            for x in self.conf['rdf.graph'].query(query_stmt):
                yield x

    def identifier(self):
        """
        Note that this identifier changes with every change to the fields
        For example, the identifiers may be distinct for two evidence objects with the same
        pubmed id. This is because manual addition of fields is allowed: an 'asserts' may
        be saying something in addition to the article which is referenced by the pmid.
        """
        return self.conf['molecule_name'](self._fields)

    def _wormbase_extract(self):
        # Extract data from wormabase
        def wbRequest(ident,field):
            import urllib2 as U
            import json
            headers = {'Content-Type': 'application/json'}
            r = U.Request("http://api.wormbase.org/rest/widget/paper/"+wbid+"/"+field, headers=headers)
            s = U.urlopen(r)
            return json.load(s)

        wbid = self._fields['wormbase']
        # get the author
        j = wbRequest(wbid, 'authors')
        self._fields['author'] = [x['label'] for x in j['fields']['data']]
        # get the publication date
        j = wbRequest(wbid, 'publication_date')
        self._fields['publication_date'] = j['fields']['name']

    def _crossref_doi_extract(self):
        # Extract data from wormabase
        def crRequest():
            import urllib2 as U2
            import urllib as U
            import json
            headers = {'Content-Type': 'application/json'}
            data = {'q': doi}
            data_encoded = U.urlencode(data)
            r = U2.Request('http://search.labs.crossref.org/dois?%s' % data_encoded , headers=headers)
            s = U2.urlopen(r)
            return json.load(s)
        return crRequest()

    def author(self,v=False):
        """
        Get/set the author for this evidence object
        """
        if v:
            self._fields['author'] = v
        else:
            if 'author' in self._fields:
                return self._fields['author']
            else:
                return []

    def year(self, v=False):
        if v:
            self._fields['publication_date'] = v
        else:
            if 'publication_date' in self._fields:
                return self._fields['publication_date']
            else:
                return ''
    def __eq__(self, other):
        for f in self._fields:
            if (f not in other._fields) or (self._fields(f) != other._fields(f)):
                return False
        return True
