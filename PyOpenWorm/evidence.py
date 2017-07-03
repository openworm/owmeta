from PyOpenWorm.pProperty import Property
from PyOpenWorm.dataObject import DataObject
from six.moves.urllib.parse import urlparse, unquote, urlencode
from six.moves.urllib.request import Request, urlopen
from six.moves.urllib.error import HTTPError, URLError
import logging
import traceback
import re

logger = logging.getLogger(__file__)

class EvidenceError(Exception):
    pass


def _pubmed_uri_to_pmid(uri):
    parsed = urlparse(uri)
    pmid = int(parsed.path.split("/")[2])
    return pmid


def _doi_uri_to_doi(uri):
    parsed = urlparse(uri)
    doi = parsed.path.split("/")[1]
    # the doi from a url needs to be decoded
    doi = unquote(doi)
    return doi


def _url_request(url, headers={}):
    try:
        r = Request(url, headers=headers)
        s = urlopen(r, timeout=1)
        info = dict(s.info())
        content_type = {k.lower() : info[k] for k in info} ['content-type']
        md = re.search("charset *= *([^ ]+)", content_type)
        if md:
            s.charset = md.group(1)

        return s
    except HTTPError:
        return ""
    except URLError:
        return ""


def _json_request(url):
    import json
    headers = {'Content-Type': 'application/json'}
    try:
        data = _url_request(url, headers).read().decode('UTF-8')
        if hasattr(data, 'charset'):
            return json.loads(data, encoding=data.charset)
        else:
            return json.loads(data)
    except BaseException:
        logger.warning("Couldn't retrieve JSON data from " + url,
                       exc_info=True)
        return {}


class AssertsAllAbout(Property):
    # TODO: Needs tests!
    multiple = True
    linkName = "asserts_all_about"

    def __init__(self, **kwargs):
        Property.__init__(self, 'asserts_all_about', **kwargs)

    @property
    def values(self):
        return []

    def set(self, o, **kwargs):
        """Establish the "asserts" relationship for all of the properties of the given object"""
        self.owner.asserts(o)
        for p in o.properties:
            self.owner.asserts(p)

    def get(self, **kwargs):
        # traverse the hierarchy of ObjectProperties and return all of the
        # asserts relationships...
        ns = {"ow": self.base_namespace,
              "ns1": self.rdf_namespace,
              "ev": self.base_namespace["Evidence"] + "/",
              "ns2": self.base_namespace["SimpleProperty"] + "/"
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
        # XXX: All triples here are from ``asserts``
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

    def __init__(
            self,
            conf=False,
            author=None,
            uri=None,
            year=None,
            date=None,
            title=None,
            doi=None,
            wbid=None,
            wormbaseid=None,
            wormbase=None,
            bibtex=None,
            pmid=None,
            pubmed=None,
            **kwargs):
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
        super(Evidence,self).__init__(conf=conf, **kwargs)
        self._fields = dict()
        Evidence.ObjectProperty('asserts', multiple=True, owner=self)
        AssertsAllAbout(owner=self)

        multivalued_fields = ('author', 'uri')
        other_fields = ('year', 'title', 'doi', 'wbid', 'pmid')
        self.id_precedence = ('doi', 'pmid', 'wbid', 'uri')
        for x in multivalued_fields:
            Evidence.DatatypeProperty(x, multiple=True, owner=self)

        for x in other_fields:
            Evidence.DatatypeProperty(x, owner=self)

        if pmid is not None:
            self._fields['pmid'] = pmid
        elif pubmed is not None:
            self._fields['pmid'] = pubmed

        if 'pmid' in self._fields:
            self._pubmed_extract()
            self.pmid(self._fields['pmid'])

        if wbid is not None:
            self._fields['wormbase'] = wbid
        elif wormbase is not None:
            self._fields['wormbase'] = wormbase
        elif wormbaseid is not None:
            self._fields['wormbase'] = wormbaseid

        if 'wormbase' in self._fields:
            self._wormbase_extract()
            self.wbid(self._fields['wormbase'])

        if doi is not None:
            self._fields['doi'] = doi
            self._crossref_doi_extract()
            self.doi(doi)

        if bibtex is not None:
            self._fields['bibtex'] = bibtex

        if year is not None:
            self.year(year)
        elif date is not None:
            self.year(date)

        if title is not None:
            self.title(title)

        if author is not None:
            self.author(author)

        if uri is not None:
            self.uri(uri)

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
        dp = Evidence.DatatypeProperty(k, owner=self)
        dp(v)

    @property
    def defined(self):
        if super(Evidence, self).defined:
            return True
        else:
            for x in self.id_precedence:
                if getattr(self, x).has_defined_value():
                    return True

    def identifier(self):
        if super(Evidence, self).defined:
            return super(Evidence, self).identifier()
        for idKind in self.id_precedence:
            idprop = getattr(self, idKind)
            if idprop.has_defined_value():
                s = str(idKind) + ":" + idprop.defined_values[0].identifier().n3()
                return self.make_identifier(s)

    # Each 'extract' method should attempt to fill in additional fields given which ones
    # are already set as well as correct fields that are wrong
    # TODO: Provide a way to override modification of already set values.
    def _wormbase_extract(self):
        # XXX: wormbase's REST API is pretty sparse in terms of data provided.
        #     Would be better off using AQL or the perl interface
        # _Very_ few of these have these fields filled in
        wbid = self._fields['wormbase']

        def wbRequest(ident, field):
            return _json_request(
                "http://api.wormbase.org/rest/widget/paper/" +
                wbid +
                "/" +
                field)
        # get the author
        try:
            j = wbRequest(wbid, 'authors')
        except Exception:
            logger.warning("Couldn't retrieve Wormbase authors", exc_info=True)
            return

        if 'fields' in j:
            f = j['fields']
            if 'data' in f:
                self.author([x['label'] for x in f['data']])
            elif 'name' in f:
                self.author(f['name']['data']['label'])

        # get the publication date
        try:
            j = wbRequest(wbid, 'publication_date')
        except Exception:
            logger.warning("Couldn't retrieve Wormbase publication date",
                           exc_info=True)
            return
        if 'fields' in j:
            f = j['fields']
            if 'data' in f:
                self.year(f['data']['label'])
            elif 'name' in f:
                self.year(f['name']['data']['label'])

    def _crossref_doi_extract(self):
        # Extract data from crossref
        def crRequest(doi):
            data = {'q': doi}
            data_encoded = urlencode(data)
            return _json_request(
                'http://search.labs.crossref.org/dois?%s' %
                data_encoded)

        doi = self._fields['doi']
        if doi[:4] == 'http':
            doi = _doi_uri_to_doi(doi)
        try:
            r = crRequest(doi)
        except Exception:
            logger.warning("Couldn't retrieve Crossref info", exc_info=True)
            return
        # XXX: I don't think coins is meant to be used, but it has structured
        # data...
        if len(r) > 0:
            extra_data = r[0]['coins'].split('&amp;')
            fields = (x.split("=") for x in extra_data)
            fields = [[y.replace('+', ' ').strip() for y in x] for x in fields]
            authors = [x[1] for x in fields if x[0] == 'rft.au']
            for a in authors:
                self.author(a)
            # no error for bad ids, just an empty list
            if len(r) > 0:
                # Crossref can process multiple doi's at one go and return the
                # metadata. we just need the first one
                r = r[0]
                if 'title' in r:
                    self.title(r['title'])
                if 'year' in r:
                    self.year(r['year'])

    def _pubmed_extract(self):
        def pmRequest(pmid):
            import xml.etree.ElementTree as ET  # Python 2.5 and up
            base = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
            # XXX: There's more data in esummary.fcgi?, but I don't know how to
            # parse it
            url = base + "esummary.fcgi?db=pubmed&id=%d" % pmid
            s = _url_request(url)
            if hasattr(s, 'charset'):
                parser = ET.XMLParser(encoding=s.charset)
            else:
                parser = None

            return ET.parse(s, parser)

        pmid = self._fields['pmid']
        if pmid[:4] == 'http':
            # Probably a uri, right?
            pmid = _pubmed_uri_to_pmid(pmid)
        pmid = int(pmid)

        try:
            tree = pmRequest(pmid)
        except Exception:
            logger.warning("Couldn't retrieve Pubmed info", exc_info=True)
            return

        for x in tree.findall('./DocSum/Item[@Name="AuthorList"]/Item'):
            self.author(x.text)
