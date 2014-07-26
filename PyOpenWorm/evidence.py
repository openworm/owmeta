"""
.. class:: Evidence

    An Evidence object represents a single document

Created on Sun Feb 23 17:10:53 2014

@author: slarson
@author: mwatts15


"""
from PyOpenWorm import *

class EvidenceError(Exception):
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

def _url_request(url,headers={}):
    import urllib2 as U
    try:
        r = U.Request(url, headers=headers)
        s = U.urlopen(r)
        return s
    except U.HTTPError:
        return ""
    except U.URLError:
        return ""

def _json_request(url):
    import json
    headers = {'Content-Type': 'application/json'}
    try:
        return json.load(_url_request(url,headers))
    except BaseException:
        return {}

class Evidence(DataObject):
    """
    A class for storing metadata, like scholarly references, for
    other objects
    Attributes
    ----------
    asserts : ObjectProperty (value_type=DataObject)
       Something asserted by this evidence

    Parameters
    ----------
    doi : string
        A Digital Object Identifier (DOI) that provides evidence, optional
    pmid : string
        A PubMed ID (PMID) that point to a paper that provides evidence, optional
    wormbaseid : string
        An ID from WormBase that points to a record that provides evidence, optional
    author : string
        The author of the evidence
    title : string
        The title of the evidence
    year : string or int
        The date (e.g., publication date) of the evidence
    """
    def __init__(self, conf=False, **source):
        # The type of the evidence (a paper, a lab, a uri) is
        # determined by the `source` key
        # We keep track of a set of fields for the evidence.
        # Some of the fields are pulled from provided URIs and
        # some is provided by the user.
        #
        # Turns into a star graph
        #
        # Evidence field1 value1
        #        ; field2 value2
        #        ; field3 value3 .
        DataObject.__init__(self, conf=conf)
        self._fields = dict()
        ObjectProperty('asserts', owner=self)
        DatatypeProperty('author',owner=self)
        DatatypeProperty('year',owner=self)
        DatatypeProperty('title',owner=self)
        DatatypeProperty('doi',owner=self)
        DatatypeProperty('wbid',owner=self)
        DatatypeProperty('pmid',owner=self)
        DatatypeProperty('uri',owner=self)

        #XXX: I really don't like putting these in two places
        for k in source:
            if k in ('pubmed', 'pmid'):
                self._fields['pmid'] = source[k]
                self._pubmed_extract()
                self.pmid(source[k])
            if k in ('wormbaseid','wormbase', 'wbid'):
                self._fields['wormbase'] = source[k]
                self._wormbase_extract()
                self.wbid(source[k])
            if k in ('doi',):
                self._fields['doi'] = source[k]
                self._crossref_doi_extract()
                self.doi(source[k])
            if k in ('bibtex',):
                self._fields['bibtex'] = source[k]
            if k in (x.linkName for x in self.properties):
                getattr(self,k)(source[k])

    def add_data(self, k, v):
        """ Add a field

        Parameters
        ----------
        k : string
            Field name
        v : string
            Field value
        """
        self._fields[k] = v
        dp = DatatypeProperty(k,owner=self)
        dp(v)

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
        for a in authors:
            self.author(a)
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
            try: import lxml.etree as ET
            except ImportError:
                try: import cElementTree as ET
                except ImportError:
                    try: import elementtree.ElementTree as ET
                    except ImportError:
                        import xml.etree.ElementTree as ET # Python 2.5 and up
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
        for x in tree.xpath('/eSummaryResult/DocSum/Item[@Name="AuthorList"]/Item'):
            self.author(x.text)
