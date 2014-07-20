# vim: set fileencoding=utf-8 :
import unittest
import neuroml
import neuroml.writers as writers
import sys
sys.path.insert(0,".")
import PyOpenWorm
from PyOpenWorm import *
import networkx
import rdflib
import rdflib as R
import pint as Q
import os

try:
    import bsddb
    has_bsddb = True
except ImportError:
    has_bsddb = False

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
        # Set do_logging to True if you like walls of text
        PyOpenWorm.connect(conf=self.config, do_logging=True)
        self.config.openDatabase()
    def tearDown(self):
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
        w = Worm()
        w.neuron_network(Network())
        w.save()
        self.assertIsInstance(Worm().get_neuron_network(), Network)

    def test_muscles1(self):
        w = Worm()
        w.muscle(Muscle(name='MDL08'))
        w.muscle(Muscle(name='MDL15'))
        w.save()
        self.assertIn(Muscle(name='MDL08'), list(Worm().muscles()))
        self.assertIn(Muscle(name='MDL15'), list(Worm().muscles()))

    def test_get_semantic_net(self):
        g0 = Worm().get_semantic_net()
        self.assertTrue(isinstance(g0, rdflib.ConjunctiveGraph))

class ConfigureTest(unittest.TestCase):
    def test_fake_config(self):
        """ Try to retrieve a config value that hasn't been set """
        with self.assertRaises(KeyError):
            c = Configure()
            c['not_a_valid_config']

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
            Data.open("tests/bad_test.conf")

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
        c.save()
        self.assertEqual(["AB plapaaaapp"], list(Cell(name="ADAL").lineageName()))

    def test_same_name_same_id(self):
        """
        Test that two Cell objects with the same name have the same identifier()
        Saves us from having too many inserts of the same object.
        """
        c = Cell(name="boots")
        c1 = Cell(name="boots")
        self.assertEqual(c.identifier(),c1.identifier())
    @unittest.skip('Long runner')
    def test_morphology_is_NeuroML_morphology(self):
        """ Check that the morphology is the kind made by neuroml """
        c = Cell(name="ADAR",conf=self.config)
        # get the morph
        m = c.morphology()
        self.assertIsInstance(m, neuroml.Morphology)

    @unittest.skip('Long runner')
    def test_morphology_validates(self):
        """ Check that we can generate a cell's file and have it validate """
        # Load in raw morphology for ADAL
        self.config['rdf.graph'].parse("PVDR.nml.rdf.xml",format='trig')
        n = Neuron(name='PVDR', conf=self.config)
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

    @unittest.skip("Should be tracked by version control")
    def test_uploader(self):
        """ Make sure that we're marking a statement with it's uploader """
        g = make_graph(20)
        r = DataObject(triples=g,conf=self.config)
        r.save()
        u = r.uploader()
        self.assertEqual(self.config['user.email'], u)

    def test_object_from_id(self):
        do = DataObject(ident="http://example.org")
        g = do.object_from_id('http://openworm.org/entities/Neuron')
        self.assertIsInstance(g,Neuron)
        g = do.object_from_id('http://openworm.org/entities/Connection')
        self.assertIsInstance(g,Connection)

    @unittest.skip("Should be tracked by version control")
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
            DataUser()

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
    @unittest.skip("Should be tracked by version control")
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
        self.neur = lambda x : Neuron(name=x)

    def test_Cell(self):
        do = self.neur('BDUL')
        self.assertTrue(isinstance(do,Cell))

    def test_receptors(self):
        n = self.neur('AVAL')
        n.receptor('GLR-2')
        n.save()
        self.assertIn('GLR-2', list(self.neur('AVAL').receptors()))

    def test_same_name_same_id(self):
        """
        Test that two Neuron objects with the same name have the same identifier()
        Saves us from having too many inserts of the same object.
        """
        c = Neuron(name="boots")
        c1 = Neuron(name="boots")
        self.assertEqual(c.identifier(query=True),c1.identifier(query=True))

    def test_type(self):
        n = self.neur('AVAL')
        n.type('interneuron')
        n.save()
        self.assertIn('interneuron', list(self.neur('AVAL').type()))

    def test_name(self):
        """ Test that the name property is set when the neuron is initialized with it """
        self.assertEqual(next(self.neur('AVAL').name()), 'AVAL')
        self.assertEqual(next(self.neur('AVAR').name()), 'AVAR')

    def test_neighbor(self):
        n0 = self.neur('AVAR')
        n = self.neur('AVAL')
        n.neighbor(self.neur('PVCL'))
        neighbors = list(n.neighbor())
        self.assertIn(self.neur('PVCL'),neighbors)
        n.save()
        self.assertIn(self.neur('PVCL'), list(self.neur('AVAL').neighbor()))

    def test_init_from_lineage_name(self):
        c = Neuron(lineageName="AB plapaaaap",name="ADAL")
        c.save()
        c = Neuron(lineageName="AB plapaaaap")
        self.assertEqual(next(c.name()), 'ADAL')

    def test_GJ_degree(self):
        self.assertEqual(self.neur('AVAL').GJ_degree(),60)

    def test_Syn_degree(self):
        self.assertEqual(self.neur('AVAL').Syn_degree(),74)

class NetworkTest(_DataTest):
    def setUp(s):
        _DataTest.setUp(s)
        s.net = Network(conf=s.config)

    def test(self):
        self.assertTrue(isinstance(self.net,Network))

    def test_aneuron(self):
        self.assertTrue(isinstance(self.net.aneuron('AVAL'),PyOpenWorm.Neuron))

    def test_neurons(self):
        self.net.neuron(Neuron(name='AVAL'))
        self.net.neuron(Neuron(name='DD5'))
        self.assertTrue('AVAL' in self.net.neurons())
        self.assertTrue('DD5' in self.net.neurons())

    def test_synapses_rdf(self):
        """ Check that synapses() returns connection objects """
        for x in self.net.synapse():
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
        self.assertEqual(u"Jean César", next(Evidence(bibtex=bibtex).author()))

    def test_pubmed_init1(self):
        """
        A pubmed uri
        """
        uri = "http://www.ncbi.nlm.nih.gov/pubmed/24098140?dopt=abstract"
        self.assertIn(u"Frédéric MY", list(Evidence(pmid=uri).author()))

    def test_pubmed_init2(self):
        """
        A pubmed id
        """
        pmid = "24098140"
        self.assertIn(u"Frédéric MY", list(Evidence(pmid=pmid).author()))

    def test_pubmed_multiple_authors_list(self):
        """
        When multiple authors are on a paper, all of their names sohuld be returned in an iterator. Publication order not necessarily preserved
        """
        pmid = "24098140"
        alist = [u"Frédéric MY","Lundin VF","Whiteside MD","Cueva JG","Tu DK","Kang SY","Singh H","Baillie DL","Hutter H","Goodman MB","Brinkman FS","Leroux MR"]
        self.assertEqual(set(alist), set(Evidence(pmid=pmid).author()))

    def test_doi_init1(self):
        """
        Full dx.doi.org uri
        """
        self.assertEqual([u'Elizabeth R. Chen', u'Michael Engel', u'Sharon C. Glotzer'], list(Evidence(doi='http://dx.doi.org/10.1007%2Fs00454-010-9273-0').author()))
    def test_doi_init2(self):
        """
        Just the identifier, no URI
        """
        self.assertEqual([u'Elizabeth R. Chen', u'Michael Engel', u'Sharon C. Glotzer'], list(Evidence(doi='10.1007/s00454-010-9273-0').author()))
    @unittest.skip("Fix later")
    def test_doi_init_fail_on_request_prefix(self):
        """
        Requesting only the prefix
        """
        with self.assertRaises(EvidenceError):
            Evidence(doi='http://dx.doi.org/10.1126')
    @unittest.skip("Fix later")
    def test_doi_init_fail_on_request_suffix(self):
        """
        Requesting only the prefix
        """
        with self.assertRaises(EvidenceError):
            Evidence(doi='http://dx.doi.org/s00454-010-9273-0')

    def test_wormbase_init(self):
        """ Initialize with wormbase source """
        # Wormbase lacks anything beyond the author,date format for a lot of papers
        self.assertIn(u'Frederic et al., 2013', list(Evidence(wormbase="WBPaper00044287").author()))

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
        r.identifier = lambda **args : r.make_identifier("test")
        e.save()
        l = list(e.asserts())
        self.assertIn(r,l)

class RDFLibTest(unittest.TestCase):
    """Test for RDFLib."""

    @classmethod
    def setUpClass(cls):
        cls.ns = {"ns1" : "http://example.org/"}
    def test_uriref_not_url(self):
        try:
            rdflib.URIRef("daniel@example.com")
        except:
            self.fail("Doesn't actually fail...which is weird")
    def test_uriref_not_id(self):
        import cStringIO
        out = cStringIO.StringIO()
        #XXX: capture the logged warning
        rdflib.URIRef("some random string")
    def test_BNode_equality1(self):
        a = rdflib.BNode("some random string")
        b = rdflib.BNode("some random string")
        self.assertEqual(a, b)
    def test_BNode_equality2(self):
        a = rdflib.BNode()
        b = rdflib.BNode()
        self.assertNotEqual(a, b)

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
        self.assertIsInstance(next(c.pre_cell()), Neuron)
        self.assertIsInstance(next(c.post_cell()), Neuron)
        self.assertEqual(next(c.number()), 3)
        self.assertEqual(next(c.syntype()), 'send')
        self.assertEqual(next(c.synclass()), 'Serotonin')

    def test_init_number_is_a_number(self):
        with self.assertRaises(Exception):
            Connection(1,2,"gazillion",4,5)

    def test_init_with_neuron_objects(self):
        n1 = Neuron(name="AVAL")
        n2 = Neuron(name="PVCR")
        try:
            Connection(n1,n2)
        except:
            self.fail("Shouldn't fail on Connection init")

    def test_load1(self):
        """ Put the appropriate triples in. Try to load them """
        g = R.Graph()
        self.config['rdf.graph'] = g
        for t in self.trips:
            g.add(t)
        c = Connection(conf=self.config)
        for x in c.load():
            self.assertIsInstance(x,Connection)

    def test_load_with_filter(self):
        # Put the appropriate triples in. Try to load them
        g = R.Graph()
        self.config['rdf.graph'] = g
        for t in self.trips:
            g.add(t)
        c = Connection(pre_cell="PVCR", conf=self.config)
        r = c.load()
        for x in r:
            self.assertIsInstance(x,Connection)

class MuscleTest(_DataTest):

    def test_muscle(self):
        self.assertTrue(isinstance(Muscle(name='MDL08'), Muscle))

    def test_muscle_neurons(self):
        m = Muscle(name='MDL08')
        neu = Neuron(name="tnnetenba")
        m.neurons(neu)
        m.save()
        m = Muscle(name='MDL08')
        self.assertIn(neu, list(m.neurons()))

class DataTest(_DataTest):
    def test_sleepy_cat_source(self):
        """ May fail if bsddb is not available. Ignore if it is not """
        # open the database
        # check we can add a triple
        try:
            self.config['source'] = 'Sleepycat'
            self.config['rdf.store'] = 'Sleepycat'
            self.config['rdf.store_conf'] = 'test.db'

            g = self.config['rdf.graph']
            ns = self.config['rdf.namespace']
            g.add((ns['64'], ns['356'], ns['184']))
            b = g.query("ASK { ?S ?P ?O }")
            for x in b:
                self.assertTrue(x)
            self.config['rdf.graph'].close()
        except ImportError:
            pass
    def test_trix_source(self):
        """ May fail if bsddb is not available. Ignore if it is not """
        try:
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
        except ImportError:
            pass

class PropertyTest(_DataTest):
    pass
class SimplePropertyTest(_DataTest):
    def __init__(self,*args,**kwargs):
        _DataTest.__init__(self,*args,**kwargs)
        id_tests = []

    # XXX: auto generate some of these tests...
    def test_same_value_same_id_empty(self):
        """
        Test that two SimpleProperty objects with the same name have the same identifier()
        """
        do = DataObject(ident=R.URIRef("http://example.org"))
        do1 = DataObject(ident=R.URIRef("http://example.org"))
        c = DatatypeProperty("boots", do)
        c1 = DatatypeProperty("boots", do1)
        self.assertEqual(c.identifier(),c1.identifier())

    def test_same_value_same_id_not_empty(self):
        """
        Test that two SimpleProperty with the same name have the same identifier()
        """
        do = DataObject(ident=R.URIRef("http://example.org"))
        do1 = DataObject(ident=R.URIRef("http://example.org"))
        c = DatatypeProperty("boots", do)
        c1 = DatatypeProperty("boots", do1)
        do.boots('partition')
        do1.boots('partition')
        self.assertEqual(c.identifier(),c1.identifier())

    def test_same_value_same_id_not_empty_object_property(self):
        """
        Test that two SimpleProperty with the same name have the same identifier()
        """
        do = DataObject(ident=R.URIRef("http://example.org"))
        do1 = DataObject(ident=R.URIRef("http://example.org"))
        dz = DataObject(ident=R.URIRef("http://example.org/vip"))
        dz1 = DataObject(ident=R.URIRef("http://example.org/vip"))
        c = ObjectProperty("boots", do)
        c1 = ObjectProperty("boots", do1)
        do.boots(dz)
        do1.boots(dz1)
        self.assertEqual(c.identifier(),c1.identifier())

    def test_diff_value_diff_id_not_empty(self):
        """
        Test that two SimpleProperty with the same name have the same identifier()
        """
        do = DataObject(ident=R.URIRef("http://example.org"))
        do1 = DataObject(ident=R.URIRef("http://example.org"))
        c = DatatypeProperty("boots", do)
        c1 = DatatypeProperty("boots", do1)
        do.boots('join')
        do1.boots('partition')
        self.assertNotEqual(c.identifier(),c1.identifier())

    def test_diff_prop_same_name_same_object_same_value_same_id(self):
        """
        Test that two SimpleProperty with the same name have the same identifier()
        """
        # why would you ever do this?
        do = DataObject(ident=R.URIRef("http://example.org"))
        c = DatatypeProperty("boots", do)
        c1 = DatatypeProperty("boots", do)
        c('join')
        c1('join')
        self.assertEqual(c.identifier(),c1.identifier())

    def test_diff_prop_same_name_same_object_diff_value_same_id(self):
        """
        Test that two SimpleProperty with the same name have the same identifier()
        """
        # why would you ever do this?
        do = DataObject(ident=R.URIRef("http://example.org"))
        c = DatatypeProperty("boots", do)
        c1 = DatatypeProperty("boots", do)
        c('partition')
        c1('join')
        self.assertNotEqual(c.identifier(),c1.identifier())

    def test_diff_value_insert_order_same_id(self):
        """
        Test that two SimpleProperty with the same name have the same identifier()
        """
        do = DataObject(ident=R.URIRef("http://example.org"))
        do1 = DataObject(ident=R.URIRef("http://example.org"))
        c = DatatypeProperty("boots", do)
        c1 = DatatypeProperty("boots", do1)
        do.boots('join')
        do.boots('simile')
        do.boots('partition')
        do1.boots('partition')
        do1.boots('join')
        do1.boots('simile')
        self.assertEqual(c.identifier(),c1.identifier())

    def test_diff_value_insert_order_same_id_object_property(self):
        """
        Test that two SimpleProperty with the same name have the same identifier()
        """
        do = DataObject(ident=R.URIRef("http://example.org"))
        do1 = DataObject(ident=R.URIRef("http://example.org"))
        oa = DataObject(ident=R.URIRef("http://example.org/a"))
        ob = DataObject(ident=R.URIRef("http://example.org/b"))
        oc = DataObject(ident=R.URIRef("http://example.org/c"))

        c = ObjectProperty("boots", do)
        c1 = ObjectProperty("boots", do1)

        do.boots(oa)
        do.boots(ob)
        do.boots(oc)
        do1.boots(oc)
        do1.boots(oa)
        do1.boots(ob)
        self.assertEqual(c.identifier(),c1.identifier())

    def test_triples_with_no_value(self):
        """ Test that when there is no value set for a property, it still yields triples """
        do = DataObject(ident=R.URIRef("http://example.org"))
        class T(SimpleProperty):
            property_type = 'DatatypeProperty'
            linkName = 'test'

        sp = T(owner=do)
        self.assertNotEqual(len(list(sp.triples())), 0)
        self.assertNotEqual(len(list(sp.triples(query=True))), 0)

class NeuroMLTest(_DataTest):
    pass
