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
        s = U.urlopen(r, timeout=1)
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

class AssertsAllAbout(Property):
    # TODO: Needs tests!
    multiple=True
    def __init__(self, **kwargs):
        Property.__init__(self, 'asserts_all_about', **kwargs)

    def set(self, o, **kwargs):
        """Establish the "asserts" relationship for all of the properties of the given object"""
        self.owner.asserts(o)
        for p in o.properties:
            self.owner.asserts(p)

    def get(self, **kwargs):
        # traverse the hierarchy of ObjectProperties and return all of the asserts relationships...
        ns = { "ow": self.base_namespace,
               "ns1" : self.rdf_namespace,
               "ev": self.base_namespace["Evidence"] + "/",
               "ns2" : self.base_namespace["SimpleProperty"] + "/"
             }
        q = """
        SELECT ?DataObject ?x ?prop WHERE
        {
            ?DataObject rdf:type ow:DataObject .
            ?DataObject ?x ?DataObject_prop .
            ?DataObject_prop sp:value ?prop .
            ?Evidence ev:asserts ?Evidence_asserts .
            filter (EXISTS { ?DataObject_prop rdf:type ow:Property . })
        # object
        # asserts property pattern
        # general property pattern
        }
        """

    def triples(self, **kwargs):
        #XXX: All triples here are from ``asserts``
        return []

class Evidence(DataObject):
    """
    A representation of some document which provides evidence like scholarly
    references, for other objects.

    Possible keys include::

        pmid,pubmed: a pubmed id or url (e.g., 24098140)
        wbid,wormbase: a wormbase id or url (e.g., WBPaper00044287)
        doi: a Digitial Object id or url (e.g., s00454-010-9273-0)

    Attaching evidence
    -------------------
    Attaching evidence to an object is as easy as::

          e = Evidence(author='White et al.', date='1986')
          e.asserts(Connection(pre_cell="VA11", post_cell="VD12"))
          e.save()

    But what does this series of statements mean? For us it means that White et al.
    assert that "the cells VA11 and VD12 have a connection".
    In particular, it says nothing about the neurons themselves.

    Another example::

          e = Evidence(author='Sulston et al.', date='1983')
          e.asserts(Neuron(name="AVDL").lineageName("AB alaaapalr"))
          e.save()

    This would say that Sulston et al. claimed that neuron AVDL has lineage AB alaaapalr.

    Now a more ambiguous example::

          e = Evidence(author='Sulston et al.', date='1983')
          e.asserts(Neuron(name="AVDL"))
          e.save()

    What might this mean? There's no clear relationship being discussed as in the
    previous examples. There are two reasonable semantics for
    these statements. They could indicate that Sulston et al. assert everything
    about the AVDL (in this case, only its name). Or they could
    indicate that Sulston et al. state the existence of AVDL. We will assume the
    semantics of the latter for *most* objects. The second
    intention can be expressed as::

          e = Evidence(author='Sulston et al.', date='1983')
          e.asserts_all_about(Neuron(name="AVDL"))
          e.save()

    `asserts_all_about` individually asserts each of the properties of the Neuron
    including its existence. It does not recursively assert
    properties of values set on the AVDL Neuron. If, for instance, the Neuron had a
    *complex object* as the value for its receptor types with
    information about the receptor's name primary agonist, etc., `asserts_all_about`
      would say nothing about these. However, `asserts_all` (TODO)::

          e.asserts_all(Neuron(name="AVDL",receptor=complex_receptor_object))

    would make the aforementioned recursive statement.

    Retrieving evidence
    -------------------

    .. Not tested with the latest

    Retrieving evidence for an object is trivial as well ::

          e = Evidence()
          e.asserts(Connection(pre_cell="VA11", post_cell="VD12"))
          for x in e.load():
             print x

    This would print all of the evidence for the connection between VA11 and VD12

    It's important to note that the considerations of recursive evidence assertions
    above do not operate for retrieval. Only evidence for the
    particular object queried (the Connection in the example above), would be
    returned and not any evidence for anything otherwise about VA11
    or VD12.

    Attributes
    ----------
    asserts : ObjectProperty (value_type=DataObject)
       When used with an argument, state that this Evidence asserts that the
       relationship is true.

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

       When used without arguments, returns a sequence of statements asserted by
       this evidence

       Example::

           import bibtex
           bt = bibtex.parse("my.bib")
           n1 = Neuron("AVAL")
           n2 = Neuron("DA3")
           c = Connection(pre=n1,post=n2,class="synapse")
           e = Evidence(bibtex=bt['white86'])
           e.asserts(c)
           list(e.asserts()) # Returns a list [..., d, ...] such that d==c
    doi : DatatypeProperty
        A Digital Object Identifier (DOI) that provides evidence, optional
    pmid : DatatypeProperty
        A PubMed ID (PMID) that point to a paper that provides evidence, optional
    wormbaseid : DatatypeProperty
        An ID from WormBase that points to a record that provides evidence, optional
    author : DatatypeProperty
        The author of the evidence
    title : DatatypeProperty
        The title of the evidence
    year : DatatypeProperty
        The date (e.g., publication date) of the evidence
    uri : DatatypeProperty
        A URL that points to evidence

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
    uri : string
        A URL that points to evidence
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
        Evidence.ObjectProperty('asserts', multiple=True, owner=self)
        AssertsAllAbout(owner=self)

        multivalued_fields = ('author', 'uri')

        for x in multivalued_fields:
            Evidence.DatatypeProperty(x, multiple=True, owner=self)

        other_fields = ('year',
                'title',
                'doi',
                'wbid',
                'pmid')
        fields = multivalued_fields + other_fields
        for x in other_fields:
            Evidence.DatatypeProperty(x, owner=self)

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

            if k in fields:
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
        dp = Evidence.DatatypeProperty(k,owner=self)
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
        if len(r)>0:
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

        for x in tree.findall('./DocSum/Item[@Name="AuthorList"]/Item'):
            self.author(x.text)
