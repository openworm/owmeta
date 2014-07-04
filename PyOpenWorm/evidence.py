"""
Created on Sun Feb 23 17:10:53 2014

@author: slarson
@author: mwatts15

An Evidence object represents a single document

"""
from PyOpenWorm import DataObject, Configure, Relationship, Property, SimpleProperty
import rdflib as R

class EvidenceError(BaseException):
    pass

def _pubmed_uri_to_pmid(uri):
    from urlparse import urlparse
    parsed = urlparse(uri)
    pmid = int(parsed.path.split("/")[2])
    return pmid

def _doi_uri_to_doi(uri):
    from urlparse import urlparse
    from urllib2 import unquote
    parsed = urlparse(uri)
    doi = parsed.path.split("/")[1]
    # the doi from a url needs to be decoded
    doi = unquote(doi)
    return doi
class Asserts(Property):
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
    def __init__(self,owner):
        Property.__init__(self,owner)
        self._statements = []

    def get(self):
        # Query for the evidence asserted by this
        query_stmt = "select ?g where { %s %s ?g }" % (self.owner.identifier().n3(), self.owner.rdf_namespace['asserts'].n3())
        # This returns us a bunch of triples...how do we get the objects that they represent?
        # Feed them back into a graph!
        #
        # Once we feed them into a graph, we can query on that (put this new graph in the configuration for the object)
        #
        for x in self.conf['rdf.graph'].query(query_stmt):
            g = self.object_from_id(x[0])
            if g is not None:
                yield g

    def set(self,stmt):
        assert(isinstance(stmt,Relationship))
        self._statements.append(stmt)

    def identifier(self):
        return self.rdf_type

    def triples(self):
        ident = self.owner.identifier()
        for x in self._statements:
            t = (ident, self.owner.rdf_namespace['asserts'], x.identifier())
            yield t

def _url_request(url,headers={}):
    import urllib2 as U
    try:
        r = U.Request(url, headers=headers)
        s = U.urlopen(r)
        return s
    except U.HTTPError, e:
        return ""
    except U.URLError, e:
        return ""

def _json_request(url):
    import json
    headers = {'Content-Type': 'application/json'}
    try:
        return json.load(_url_request(url,headers))
    except BaseException, e:
        return {}

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
        self.author = SimpleProperty(self,'author')
        self.year = SimpleProperty(self,'year')
        self.title = SimpleProperty(self,'title')
        self.asserts = Asserts(self)

        #XXX: I really don't like putting these in two places
        for k in source:
            if k in ('pubmed', 'pmid'):
                self._fields['pmid'] = source[k]
                self._pubmed_extract()
                break
            if k in ('wormbase', 'wbid'):
                self._fields['wormbase'] = source[k]
                self._wormbase_extract()
                break
            if k in ('doi'):
                self._fields['doi'] = source[k]
                self._crossref_doi_extract()
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

    def triples(self):
        for x in self.properties:
            for y in x.triples():
                yield y

    def identifier(self):
        """
        Note that this identifier changes with every change to the fields
        For example, the identifiers may be distinct for two evidence objects with the same
        pubmed id. This is because manual addition of fields is allowed: an 'asserts' may
        be saying something in addition to the article which is referenced by the pmid.
        """
        evidence_name = self.make_identifier("".join(x.identifier() for x in self.properties))
        return evidence_name
    # Each 'extract' method should attempt to fill in additional fields given which ones
    # are already set as well as correct fields that are wrong
    # TODO: Provide a way to override modification of already set values.
    def _wormbase_extract(self):
        #XXX: wormbase's REST API is pretty sparse in terms of data provided.
        #     Would be better off using AQL or the perl interface
        # _Very_ few of these have these fields filled in
        wbid = self._fields['wormbase']
        def wbRequest(ident,field):
            return _json_request("http://api.wormbase.org/rest/widget/paper/"+wbid+"/"+field)
        # get the author
        j = wbRequest(wbid, 'authors')
        if 'fields' in j:
            f = j['fields']
            if 'data' in f:
                self.author([x['label'] for x in f['data']])
            elif 'name' in f:
                self.author(f['name']['data']['label'])

        # get the publication date
        j = wbRequest(wbid, 'publication_date')
        if 'fields' in j:
            f = j['fields']
            if 'data' in f:
                self.year(f['data']['label'])
            elif 'name' in f:
                self.year(f['name']['data']['label'])

    def _crossref_doi_extract(self):
        # Extract data from crossref
        def crRequest(doi):
            import urllib as U
            data = {'q': doi}
            data_encoded = U.urlencode(data)
            return _json_request('http://search.labs.crossref.org/dois?%s' % data_encoded)

        doi = self._fields['doi']
        if doi[:4] == 'http':
            doi = _doi_uri_to_doi(doi)
        r = crRequest(doi)
        #XXX: I don't think coins is meant to be used, but it has structured data...
        extra_data = r[0]['coins'].split('&amp;')
        fields = (x.split("=") for x in extra_data)
        fields = [[y.replace('+', ' ').strip() for y in x] for x in fields]
        authors = [x[1] for x in fields if x[0] == 'rft.au']
        self.author(authors)
        # no error for bad ids, just an empty list
        if len(r) > 0:
            # Crossref can process multiple doi's at one go and return the metadata. we just need the first one
            r = r[0]
            if 'title' in r:
                self.title(r['title'])
            if 'year' in r:
                self.year(r['year'])

    def _pubmed_extract(self):
        def pmRequest(pmid):
            from lxml import etree as ET
            base = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
            # XXX: There's more data in esummary.fcgi?, but I don't know how to parse it
            url = base + "esummary.fcgi?db=pubmed&id=%d" % pmid
            return ET.parse(_url_request(url))

        pmid = self._fields['pmid']
        if pmid[:4] == 'http':
            # Probably a uri, right?
            pmid = _pubmed_uri_to_pmid(pmid)
        pmid = int(pmid)
        tree = pmRequest(pmid)
        self.author([x.text for x in tree.xpath('/eSummaryResult/DocSum/Item[@Name="AuthorList"]/Item')])

    def __eq__(self, other):
        for f in self._fields:
            if (f not in other._fields) or (self._fields(f) != other._fields(f)):
                return False
        return True
