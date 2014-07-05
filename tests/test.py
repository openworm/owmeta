# vim: set fileencoding=utf-8 :
import unittest
import neuroml
import neuroml.writers as writers
import sys
sys.path.insert(0,".")
import PyOpenWorm
import subprocess
from PyOpenWorm import *
import networkx
import rdflib
import rdflib as R
import pint as Q
import os

namespaces = { "rdf" : "http://www.w3.org/1999/02/22-rdf-syntax-ns#" }

# Set up the database

TestConfig = Configure.open("tests/test.conf")

def clear_graph(graph):
    graph.update("CLEAR ALL")

def make_graph(size=100):
    """ Make an rdflib graph """
    g = R.Graph()
    for i in range(size):
        s = rdflib.URIRef("http://somehost.com/s"+str(i))
        p = rdflib.URIRef("http://somehost.com/p"+str(i))
        o = rdflib.URIRef("http://somehost.com/o"+str(i))
        g.add((s,p,o))
    return g

class _DataTest(unittest.TestCase):
    def setUp(self):
        self.config = Data(TestConfig)
        self.config_no_data = TestConfig
        Configureable.default = self.config
        self.config.openDatabase()
    def tearDown(self):
        print 'closing the database'
        self.config.closeDatabase()

class WormTest(_DataTest):
    """Test for Worm."""
    def setUp(self):
        _DataTest.setUp(self)
        ns = self.config['rdf.namespace']
        self.trips = [(ns['64'], ns['356'], ns['184']),
                (ns['john'], R.RDF['type'], ns['Connection']),
                (ns['john'], ns['Connection/pre'], ns['64']),
                (ns['64'], R.RDFS['label'], R.Literal("PVCR")),
                (ns['john'], ns['Connection/syntype'], ns['356']),
                (ns['john'], ns['Connection/number'], R.Literal('1', datatype=R.XSD.integer)),
                (ns['184'], R.RDFS['label'], R.Literal("AVAL")),
                (ns['john'], ns['Connection/post'], ns['184']),
                (ns['65'], ns['356'], ns['185']),
                (ns['luke'], R.RDF['type'], ns['Connection']),
                (ns['luke'], ns['Connection/pre'], ns['65']),
                (ns['65'], R.RDFS['label'], R.Literal("PVCL")),
                (ns['luke'], ns['Connection/syntype'], ns['356']),
                (ns['luke'], ns['Connection/number'], R.Literal('1', datatype=R.XSD.integer)),
                (ns['185'], R.RDFS['label'], R.Literal("AVAR")),
                (ns['luke'], ns['Connection/post'], ns['185'])]

    def test_get_network(self):
        self.assertTrue(isinstance(Worm(self.config).get_neuron_network(), Network))

    def test_muscles(self):
        self.assertTrue('MDL08' in Worm(self.config).muscles())
        self.assertTrue('MDL15' in Worm(self.config).muscles())

    def test_get_semantic_net(self):
        g0 = Worm(self.config).get_semantic_net()
        self.assertTrue(isinstance(g0, rdflib.ConjunctiveGraph))

        qres = g0.query(
            """
            SELECT ?subLabel     #we want to get out the labels associated with the objects
            WHERE {
              GRAPH ?g { #Each triple is in its own sub-graph to enable provenance
                # match all subjects that have the 'is a' (1515) property pointing to 'muscle' (1519)
                ?subject <http://openworm.org/entities/1515> <http://openworm.org/entities/1519> .
                }
              #Triples that have the label are in the main graph only
              ?subject rdfs:label ?subLabel  #for the subject, look up their plain text label.
            }
            """)
        list = []
        for r in qres.result:
            list.append(str(r[0]))
        self.assertTrue('MDL08' in list)

class ConfigureTest(unittest.TestCase):
    def test_fake_config(self):
        """ Try to retrieve a config value that hasn't been set """
        with self.assertRaises(KeyError):
            c = Configure()
            k = c['not_a_valid_config']

    def test_literal(self):
        """ Assign a literal rather than a ConfigValue"""
        c = Configure()
        c['seven'] = "coke"
        self.assertEqual(c['seven'], "coke")

    def test_ConfigValue(self):
        """ Assign a ConfigValue"""
        c = Configure()
        class pipe(ConfigValue):
            def get(self):
                return "sign"
        c['seven'] = pipe()
        self.assertEqual("sign",c['seven'])

    def test_getter_no_ConfigValue(self):
        """ Assign a method with a "get". Should return a the object rather than calling its get method """
        c = Configure()
        class pipe:
            def get(self):
                return "sign"
        c['seven'] = pipe()
        self.assertIsInstance(c['seven'], pipe)

    def test_late_get(self):
        """ "get" shouldn't be called until the value is *dereferenced* """
        c = Configure()
        a = {'t' : False}
        class pipe(ConfigValue):
            def get(self):
                a['t'] = True
                return "sign"
        c['seven'] = pipe()
        self.assertFalse(a['t'])
        self.assertEqual(c['seven'], "sign")
        self.assertTrue(a['t'])

    def test_read_from_file(self):
        """ Read configuration from a JSON file """
        try:
            d = Data.open("tests/test.conf")
            self.assertEqual("test_value", d["test_variable"])
        except:
            self.fail("test.conf should exist and be valid JSON")
    def test_read_from_file_fail(self):
        """ Fail on attempt to read configuration from a non-JSON file """
        with self.assertRaises(BadConf):
            d = Data.open("tests/bad_test.conf")

class ConfigureableTest(unittest.TestCase):
    def test_init_empty(self):
        """Ensure Configureable gets init'd with the defalut if nothing's given"""
        i = Configureable()
        self.assertEqual(i.conf,Configureable.default)

    def test_init_False(self):
        """Ensure Configureable gets init'd with the defalut if False is given"""
        i = Configureable(conf=False)
        self.assertEqual(i.conf,Configureable.default)

class CellTest(_DataTest):

    def test_DataUser(self):
        do = Cell('',conf=self.config)
        self.assertTrue(isinstance(do,PyOpenWorm.DataUser))

    def test_lineageName(self):
        """ Test that we can retrieve the lineage name """
        c = Cell(name="ADAL",conf=self.config)
        c.lineageName("AB plapaaaapp")
        self.assertEqual(["AB plapaaaapp"], c.lineageName())

    def test_morphology_is_NeuroML_morphology(self):
        """ Check that the morphology is the kind made by neuroml """
        c = Cell(name="ADAR",conf=self.config)
        # get the morph
        m = c.morphology()
        self.assertIsInstance(m, neuroml.Morphology)

    def test_morphology_validates(self):
        """ Check that we can generate a cell's file and have it validate """
        n = Neuron(name='ADAL', conf=self.config)
        doc = PyOpenWorm.NeuroML.generate(n,1)
        writers.NeuroMLWriter.write(doc, "temp.nml")
        from neuroml.utils import validate_neuroml2
        f = sys.stdout
        try:
            sys.stdout = open(os.devnull, 'w')
        except:
            sys.stdout = f

        try:
            validate_neuroml2("temp.nml")
        except Exception, e:
            print e
            self.fail("Should validate")
        sys.stdout = f

class DataObjectTest(_DataTest):

    def test_DataUser(self):
        do = DataObject()
        self.assertTrue(isinstance(do,PyOpenWorm.DataUser))

    def test_identifier(self):
        """ Test that we can set and return an identifier """
        do = DataObject(ident="http://example.org")
        self.assertEqual(do.identifier(), R.URIRef("http://example.org"))

    def test_uploader(self):
        """ Make sure that we're marking a statement with it's uploader """
        g = make_graph(20)
        r = DataObject(triples=g,conf=self.config)
        r.save()
        u = r.uploader()
        self.assertEqual(self.config['user.email'], u)

    def test_object_from_id(self):
        g = DataObject.object_from_id('http://openworm.org/entities/Neuron')
        self.assertIsInstance(g,Neuron)
        g = DataObject.object_from_id('http://openworm.org/entities/Connection')
        self.assertIsInstance(g,Connection)

    def test_upload_date(self):
        """ Make sure that we're marking a statement with it's upload date """
        g = make_graph(20)
        r = DataObject(triples=g)
        r.save()
        u = r.upload_date()
        self.assertIsNotNone(u)


class DataUserTest(_DataTest):

    def test_init_no_config(self):
        """ Should fail to initialize since it's lacking basic configuration """
        Configureable.default = None
        with self.assertRaises(BadConf):
            do = DataUser()

    def test_init_no_config_with_default(self):
        """ Should suceed if the default configuration is a Data object """
        DataUser()

    def test_init_False_with_default(self):
        """ Should suceed if the default configuration is a Data object """
        DataUser(conf=False)

    def test_init_config_no_Data(self):
        """ Should fail if given a non-Data configuration """
        with self.assertRaises(BadConf):
            DataUser(conf=self.config_no_data)

    def test_add_statements_has_uploader(self):
        """ Assert that each statement has an uploader annotation """
        g = R.Graph()

        # Make a statement (triple)
        s = rdflib.URIRef("http://somehost.com/s")
        p = rdflib.URIRef("http://somehost.com/p")
        o = rdflib.URIRef("http://somehost.com/o")

        # Add it to an RDF graph
        g.add((s,p,o))

        # Make a datauser
        du = DataUser(self.config)

        try:
            # Add all of the statements in the graph
            du.add_statements(g)
        except Exception, e:
            self.fail("Should be able to add statements in the first place: "+str(e))

        g0 = du.conf['rdf.graph']

        # These are the properties that we should find
        uploader_n3_uri = du.conf['rdf.namespace']['uploader'].n3()
        upload_date_n3_uri = du.conf['rdf.namespace']['upload_date'].n3()
        uploader_email = du.conf['user.email']

        # This is the query to get uploader information
        q = """
        Select ?u ?t where
        {
        GRAPH ?g
        {
         <http://somehost.com/s>
         <http://somehost.com/p>
         <http://somehost.com/o> .
        }

        ?g """+uploader_n3_uri+""" ?u.
        ?g """+upload_date_n3_uri+""" ?t.
        } LIMIT 1
        """
        for x in g0.query(q):
            self.assertEqual(du.conf['user.email'],str(x['u']))

    @unittest.skip("Long runner")
    def test_add_statements_completes(self):
        g = rdflib.Graph()
        for i in range(1000):
            s = rdflib.URIRef("http://somehost.com/s%d" % i)
            p = rdflib.URIRef("http://somehost.com/p%d" % i)
            o = rdflib.URIRef("http://somehost.com/o%d" % i)
            g.add((s,p,o))
        du = DataUser(self.config)
        du.add_statements(g)

    def test_add_statements(self):
        pass

class NeuronTest(_DataTest):
    def setUp(self):
        _DataTest.setUp(self)
        self.neur = lambda x : Neuron(name=x,conf=self.config)

    def test_Cell(self):
        do = self.neur('BDUL')
        self.assertTrue(isinstance(do,Cell))

    def test_identifier(self):
        g = self.config['rdf.graph']
        self.assertEqual(self.neur('AVAL').identifier(), R.URIRef('http://openworm.org/entities/64'))
        self.assertEqual(self.neur('AWBR').identifier(), R.URIRef('http://openworm.org/entities/86'))
        self.assertEqual(self.neur('FLPR').identifier(), R.URIRef('http://openworm.org/entities/125'))
        self.assertEqual(self.neur('I6').identifier(), R.URIRef('http://openworm.org/entities/135'))
        self.assertEqual(self.neur('M5').identifier(), R.URIRef('http://openworm.org/entities/156'))
        self.assertEqual(self.neur('AUAL').identifier(), R.URIRef('http://openworm.org/entities/62'))
        self.assertEqual(self.neur('PVQL').identifier(), R.URIRef('http://openworm.org/entities/192'))
        self.assertEqual(self.neur('OLQVR').identifier(), R.URIRef('http://openworm.org/entities/167'))

    def test_receptors(self):
        self.assertTrue('GLR-2' in self.neur('AVAL').receptors())
        self.assertTrue('OSM-9' in self.neur('PHAL').receptors())

    def test_type(self):
        self.assertEqual(self.neur('AVAL').type(),'interneuron')
        self.assertEqual(self.neur('DD5').type(),'motor')
        self.assertEqual(self.neur('PHAL').type(),'sensory')

    def test_name(self):
        self.assertEqual(self.neur('AVAL').name(),'AVAL')
        self.assertEqual(self.neur('AVAR').name(),'AVAR')

    def test_init_from_lineage_name(self):
        c = Neuron(lineageName="AB plapaaaap",conf=self.config)
        self.assertEqual(c.name(), 'ADAL')

    def test_GJ_degree(self):
        self.assertEqual(self.neur('AVAL').GJ_degree(),60)

    def test_Syn_degree(self):
        self.assertEqual(self.neur('AVAL').Syn_degree(),74)

class NetworkTest(_DataTest):
    def setUp(s):
        _DataTest.setUp(s)
        s.net = Network(conf=s.config)

    def test_identifier(self):
        ident = self.net.identifier()
        self.assertEqual(self.config['rdf.namespace']["worm_net"], ident)

    def test(self):
        self.assertTrue(isinstance(self.net,Network))

    def test_aneuron(self):
        self.assertTrue(isinstance(self.net.aneuron('AVAL'),PyOpenWorm.Neuron))

    def test_neurons(self):
        self.assertTrue('AVAL' in self.net.neurons())
        self.assertTrue('DD5' in self.net.neurons())
        self.assertEqual(len(list(self.net.neurons())), 302)

    def test_synapses_rdf(self):
        """ Check that synapses() returns connection objects """
    def test_synapses_rdf(self):
        """ Check that synapses() returns connection objects """
        for x in self.net.synapses():
            self.assertIsInstance(x,Connection)
            break

    def test_as_networkx(self):
        self.assertTrue(isinstance(self.net.as_networkx(),networkx.DiGraph))

class EvidenceTest(_DataTest):
    @unittest.skip("Post alpha")
    def test_bibtex_init(self):
        bibtex = u"""@ARTICLE{Cesar2013,
          author = {Jean César},
          title = {An amazing title},
          year = {2013},
          month = jan,
          volume = {12},
          pages = {12--23},
          journal = {Nice Journal},
          abstract = {This is an abstract. This line should be long enough to test
             multilines...},
          comments = {A comment},
          keywords = {keyword1, keyword2},
        }
        """
        self.assertEqual(u"Jean César", Evidence(bibtex=bibtex).author())
    def test_triples(self):
        e = Evidence()
        e.author("Paul")
        e.title("Galatians")
        e.year("60")
        t = set((x[1],str(x[2])) for x in e.triples())
        self.assertIn((e.rdf_namespace["author"], "Paul"), t)
        self.assertIn((e.rdf_namespace["year"], "60"), t)
        self.assertIn((e.rdf_namespace["title"], "Galatians"), t)

    def test_pubmed_init1(self):
        """
        A pubmed uri
        """
        uri = "http://www.ncbi.nlm.nih.gov/pubmed/24098140?dopt=abstract"
        self.assertIn(u"Frédéric MY", Evidence(pmid=uri).author())

    def test_pubmed_init2(self):
        """
        A pubmed id
        """
        pmid = "24098140"
        self.assertIn(u"Frédéric MY", Evidence(pmid=pmid).author())

    def test_pubmed_multiple_authors_list(self):
        """
        When multiple authors are on a paper, all of their names sohuld be returned in a list (preserving order from publication!)
        """
        pmid = "24098140"
        alist = [u"Frédéric MY","Lundin VF","Whiteside MD","Cueva JG","Tu DK","Kang SY","Singh H","Baillie DL","Hutter H","Goodman MB","Brinkman FS","Leroux MR"]
        self.assertEqual(alist,Evidence(pmid=pmid).author())

    def test_doi_init1(self):
        """
        Full dx.doi.org uri
        """
        self.assertEqual([u'Elizabeth R. Chen', u'Michael Engel', u'Sharon C. Glotzer'], Evidence(doi='http://dx.doi.org/10.1007%2Fs00454-010-9273-0').author())
    def test_doi_init2(self):
        """
        Just the identifier, no URI
        """
        self.assertEqual([u'Elizabeth R. Chen', u'Michael Engel', u'Sharon C. Glotzer'], Evidence(doi='10.1007/s00454-010-9273-0').author())
    def test_doi_init_fail_on_request_prefix(self):
        """
        Requesting only the prefix
        """
        with self.assertRaises(EvidenceError):
            Evidence(doi='http://dx.doi.org/10.1126')
    def test_doi_init_fail_on_request_suffix(self):
        """
        Requesting only the prefix
        """
        with self.assertRaises(EvidenceError):
            Evidence(doi='http://dx.doi.org/s00454-010-9273-0')

    def test_wormbase_init(self):
        self.assertIn(u"Frederic, M. Y.", Evidence(wormbase="WBPaper00044287").author())

    def test_wormbase_year(self):
        """ Just make sure we can extract something without crashing """
        for i in range(600,610):
            wbid = 'WBPaper00044' + str(i)
            e = Evidence(wormbase=wbid)
            e.year()
    def test_asserts(self):
        """
        Asserting something should allow us to get it back.
        """
        e=Evidence(wormbase='WBPaper00044600')
        g = make_graph(20)
        r = Relationship(graph=g)
        e.asserts(r)
        r.identifier = lambda : r.make_identifier("test")
        e.save()
        l = list(e.asserts())
        self.assertIn(r,l)

class RDFLibTest(unittest.TestCase):
    """Test for RDFLib."""

    @classmethod
    def setUpClass(cls):
        cls.ns = {"ns1" : "http://example.org/"}
    def test_uriref_not_url(self):
        uri = rdflib.URIRef("daniel@example.com")
    def test_uriref_not_id(self):
        uri = rdflib.URIRef("some random string")
    def test_BNode_equality1(self):
        a = rdflib.BNode("some random string")
        b = rdflib.BNode("some random string")
        self.assertEqual(a, b)
    def test_BNode_equality2(self):
        a = rdflib.BNode()
        b = rdflib.BNode()
        self.assertNotEqual(a, b)

    def test_OpenRDF_reification1(self):
        """ WARNING: This test requires that you have OpenRDF installed on your machine with a repository named test and that you don't care what's in it """
        graph = R.ConjunctiveGraph(store="SPARQLUpdateStore")
        graph.open(("http://localhost:8080/openrdf-sesame/repositories/test","http://localhost:8080/openrdf-sesame/repositories/test/statements"))
        clear_graph(graph)
        update_stmt = "INSERT DATA { _:stmt ns1:subject ns1:a ; ns1:predicate ns1:b ; ns1:object ns1:c . _:someone ns1:says _:stmt }"

        for i in range(3):
            graph.update(update_stmt, initNs=self.ns)
        r = graph.query("select distinct ?z where { ?p ns1:subject ?x . ?z ns1:says ?p }", initNs=self.ns)
        self.assertEqual(3,len(r))

#class TimeTest(unittest.TestCase):
    #def test_datetime_isoformat_has_timezone(self):
        #time_stamp = now(utc).isoformat()
        #self.assertRegexpMatches(time_stamp, r'.*[+-][0-9][0-9]:[0-9][0-9]$')

class PintTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.ur = Q.UnitRegistry()
        self.Q = self.ur.Quantity
    def test_atomic_short(self):
        q = self.Q(23, "mL")
        self.assertEqual("milliliter", str(q.units))
        self.assertEqual(23, q.magnitude)

    def test_atomic_long_singular(self):
        q = self.Q(23, "milliliter")
        self.assertEqual("milliliter", str(q.units))
        self.assertEqual(23, q.magnitude)

    def test_atomic_long_plural(self):
        q = self.Q(23, "milliliters")
        self.assertEqual("milliliter", str(q.units))
        self.assertEqual(23, q.magnitude)

    def test_atomic_long_plural_to_string(self):
        #XXX: Maybe there's a way to have the unit name pluralized...
        q = self.Q(23, "milliliters")
        self.assertEqual("23 milliliter", str(q))

    def test_string_init_long_plural_to_string(self):
        #XXX: Maybe there's a way to have the unit name pluralized...
        q = self.Q("23 milliliters")
        self.assertEqual("23 milliliter", str(q))

    def test_string_init_short(self):
        q = self.Q("23 mL")
        self.assertEqual("milliliter", str(q.units))
        self.assertEqual(23, q.magnitude)

    def test_string_init_short_no_space(self):
        q = self.Q("23mL")
        self.assertEqual("milliliter", str(q.units))
        self.assertEqual(23, q.magnitude)

    def test_string_init_long_singular(self):
        q = self.Q("23 milliliter")
        self.assertEqual("milliliter", str(q.units))
        self.assertEqual(23, q.magnitude)

    def test_string_init_long_plural(self):
        q = self.Q("23 milliliters")
        self.assertEqual("milliliter", str(q.units))
        self.assertEqual(23, q.magnitude)

    def test_init_magnitude_with_string(self):
        """ Pint doesn't care if you don't give it a number """
        q = self.Q("23", "milliliters")
        self.assertEqual("milliliter", str(q.units))
        self.assertEqual("23", q.magnitude)

        q = self.Q("worm", "milliliters")
        self.assertEqual("worm", q.magnitude)

class QuantityTest(unittest.TestCase):
    def test_string_init_short(self):
        q = Quantity.parse("23 mL")
        self.assertEqual("milliliter", q.unit)
        self.assertEqual(23, q.value)

    def test_string_init_volume(self):
        q = Quantity.parse("23 inches^3")
        self.assertEqual("inch ** 3", q.unit)
        self.assertEqual(23, q.value)

    def test_string_init_compound(self):
        q = Quantity.parse("23 inches/second")
        self.assertEqual("inch / second", q.unit)
        self.assertEqual(23, q.value)

    def test_atomic_short(self):
        q = Quantity(23, "mL")
        self.assertEqual("milliliter", q.unit)
        self.assertEqual(23, q.value)

    def test_atomic_long(self):
        q = Quantity(23, "milliliters")
        self.assertEqual("milliliter", q.unit)
        self.assertEqual(23, q.value)

class RelationshipTest(_DataTest):

    def test_init_graph(self):
        """ Make sure that we're marking a statement with it's upload date """
        g = make_graph()
        r = Relationship(graph=g,conf=self.config)

    def test_rel(self):
        """ Get the relationship associated with a method """
        # XXX: Is there use case for this not covered by DataObject.load?
        s = Relationship.rel(DataObject,'uploader')

class ConnectionTest(_DataTest):
    def setUp(self):
        _DataTest.setUp(self)
        ns = self.config['rdf.namespace']
        self.trips = [(ns['64'], ns['356'], ns['184']),
                (ns['john'], R.RDF['type'], ns['Connection']),
                (ns['john'], ns['Connection/pre'], ns['64']),
                (ns['64'], R.RDFS['label'], R.Literal("PVCR")),
                (ns['john'], ns['Connection/syntype'], ns['356']),
                (ns['john'], ns['Connection/number'], R.Literal('1', datatype=R.XSD.integer)),
                (ns['184'], R.RDFS['label'], R.Literal("AVAL")),
                (ns['john'], ns['Connection/post'], ns['184']),
                (ns['65'], ns['356'], ns['185']),
                (ns['luke'], R.RDF['type'], ns['Connection']),
                (ns['luke'], ns['Connection/pre'], ns['65']),
                (ns['65'], R.RDFS['label'], R.Literal("PVCL")),
                (ns['luke'], ns['Connection/syntype'], ns['356']),
                (ns['luke'], ns['Connection/number'], R.Literal('1', datatype=R.XSD.integer)),
                (ns['185'], R.RDFS['label'], R.Literal("AVAR")),
                (ns['luke'], ns['Connection/post'], ns['185'])]

    def test_init(self):
        """Initialization with positional parameters"""
        c = Connection('AVAL','ADAR',3,'send','Serotonin')
        c.save()
        self.assertIsInstance(c.pre_cell()[0], Neuron)
        self.assertIsInstance(c.post_cell()[0], Neuron)
        self.assertEqual([3], c.number())
        self.assertEqual([], c.syntype())
        self.assertEqual([5], c.synclass())

    def test_init_number_is_a_number(self):
        with self.assertRaises(ValueError):
            Connection(1,2,"gazillion",4,5)

    def test_init_with_neuron_objects(self):
        n1 = Neuron(name="AVAL")
        n2 = Neuron(name="PVCR")
        c = Connection(n1,n2)

    def test_init_with_neuron_objects(self):
        n1 = Neuron(name="AVAL")
        n2 = Neuron(name="PVCR")
        c = Connection(n1,n2)

    def test_load1(self):
        """ Put the appropriate triples in. Try to load them """
        g = R.Graph()
        self.config['rdf.graph'] = g
        ns = self.config['rdf.namespace']
        for t in self.trips:
            g.add(t)
        c = Connection(conf=self.config)
        for x in c.load():
            self.assertIsInstance(x,Connection)

    def test_load_with_filter(self):
        # Put the appropriate triples in. Try to load them
        g = R.Graph()
        self.config['rdf.graph'] = g
        ns = self.config['rdf.namespace']
        for t in self.trips:
            g.add(t)
        c = Connection(pre_cell="PVCR", conf=self.config)
        r = c.load()

class MuscleTest(_DataTest):

    def test_muscle(self):
        self.assertTrue(isinstance(Muscle('MDL08',self.config), Muscle))

    def test_muscle_neurons(self):
        self.fail("Need an actual test")
        m = Muscle('MDL08',self.config).neurons()

class DataTest(_DataTest):
    def test_sleepy_cat_source(self):
        # open the database
        # check we can add a triple
        self.config['source'] = 'Sleepycat'
        self.config['rdf.store'] = 'Sleepycat'
        self.config['rdf.store_conf'] = 'Sleepycat'
        b = self.config['rdf.graph'].query("ASK { ?S ?P ?O }")
        for x in b:
            self.assertTrue(x)
        self.config['rdf.graph'].close()

    def test_trix_source(self):
        c = Configure().copy(self.config)
        c['rdf.source'] = 'TriX'
        c['trix_location'] = 'export.xml'
        c['rdf.store_conf'] = 'test.db'
        c['rdf.store'] = 'Sleepycat'
        d = Data(conf=c)
        d.openDatabase()
        b = d['rdf.graph'].query("ASK { ?S ?P ?O }")
        for x in b:
            self.assertTrue(x)
        d.closeDatabase()

class PropertyTest(_DataTest):
    pass

class SimplePropertyTest(_DataTest):
    def test_triples_with_no_value(self):
        """ Test that when there is no value set for a property, it doesn't yield any triples """
        do = DataObject(ident=R.URIRef("http://example.org"))
        sp = SimpleProperty(do,"test")
        for x in sp.triples():
            self.fail("Shouldn't have any triples")
    def test_get_from_database(self):
        g = R.Graph()
        ident=R.URIRef("http://example.org")
        self.config['rdf.graph'] = g
        do = DataObject(ident=ident)
        g.add((ident, do.rdf_namespace['test'], R.Literal("testvalue1")))
        g.add((ident, do.rdf_namespace['test'], R.Literal("testvalue2")))
        sp = SimpleProperty(do,"test")
        v = set(sp())
        self.assertEqual(set(["testvalue2","testvalue1"]), v)
class NeuroMLTest(_DataTest):
    pass
