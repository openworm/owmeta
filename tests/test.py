# -*- coding: utf-8 -*-

import unittest
import neuroml
import neuroml.writers as writers
import sys
sys.path.insert(0,".")
import PyOpenWorm
from PyOpenWorm import *
import test_data as TD
import networkx
import rdflib
import rdflib as R
import pint as Q
import os
import subprocess
import tempfile

USE_BINARY_DB = False
BINARY_DB = "OpenWormData/scripts/worm.db"

try:
    import bsddb
    has_bsddb = True
except ImportError:
    has_bsddb = False

namespaces = { "rdf" : "http://www.w3.org/1999/02/22-rdf-syntax-ns#" }

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
try:
    TEST_CONFIG = Configure.open("tests/_test.conf")
except:
    TEST_CONFIG = Configure.open("tests/test_default.conf")

def delete_zodb_data_store(path):
    os.unlink(path)
    os.unlink(path + '.index')
    os.unlink(path + '.tmp')
    os.unlink(path + '.lock')

class DataIntegrityTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        import csv

        cls.neurons = [] #array that holds the names of the 302 neurons at class-level scope

        if not USE_BINARY_DB:
            #use a simple graph from rdflib so we can look directly at the structure of the data
            cls.g = rdflib.Graph("ZODB") #declare class-level scope
            #load in the database
            cls.g.parse("OpenWormData/WormData.n3", format="n3")
        else:
            conf = Configure(**{ "rdf.source" : "ZODB", "rdf.store_conf" : BINARY_DB })
            PyOpenWorm.connect(conf=conf)
            cls.g = PyOpenWorm.config('rdf.graph')

        #grab the list of the names of the 302 neurons

        csvfile = open('OpenWormData/aux_data/neurons.csv', 'r')
        reader = csv.reader(csvfile, delimiter=';', quotechar='|')

        for row in reader:
            if len(row[0]) > 0: # Only saves valid neuron names
                cls.neurons.append(row[0])
    @classmethod
    def tearDownClass(cls):
        if USE_BINARY_DB:
            PyOpenWorm.disconnect()

    def testUniqueNeuronNode(self):
        """
        There should one and only one unique RDF node for every neuron.  If more than one is present for a given cell name,
        then our data is inconsistent.  If there is not at least one present, then we are missing neurons.
        """

        results = {}
        for n in self.neurons:
            #Create a SPARQL query per neuron that looks for all RDF nodes that have text matching the name of the neuron
            qres = self.g.query('SELECT distinct ?n WHERE {?n ?t ?s . ?s ?p \"' + n + '\" } LIMIT 5')
            results[n] = (len(qres.result), [x[0] for x in qres.result])

        # If there is not only one result back, then there is more than one RDF node.
        more_than_one = [(x, results[x]) for x in results if results[x][0] > 1]
        less_than_one = [(x, results[x]) for x in results if results[x][0] < 1]
        self.assertEqual(0, len(more_than_one), "Some neurons have more than 1 node: " + "\n".join(str(x) for x in more_than_one))
        self.assertEqual(0, len(less_than_one), "Some neurons have no node: " + "\n".join(str(x) for x in less_than_one))

    def testNeuronsHaveTypes(self):
        """
        Every Neuron should have a non-blank type
        """
        results = set()
        for n in self.neurons:
            qres = self.g.query('SELECT ?v WHERE { ?s <http://openworm.org/entities/SimpleProperty/value> \"' + n + '\". ' #per node ?s that has the name of a neuron associated
                                + '?k <http://openworm.org/entities/Cell/name> ?s .'
                                + '?k <http://openworm.org/entities/Neuron/type> ?o .' #look up its listed type ?o
                                + '?o <http://openworm.org/entities/SimpleProperty/value> ?v } ' #for that type ?o, get its property ?tp and its value ?v
                                )
            for x in qres:
                v = x[0]
                if isinstance(v,R.Literal):
                    results.add(n)

        # NOTE: Neurons ALNL, CANL, CANR, ALNR have unknown function and type
        self.assertEqual(len(results), len(self.neurons) - 4, "Some neurons are missing a type: {}".format(set(self.neurons) - results))

    @unittest.skip("have not yet defined asserts")
    def testWhatNodesGetTypeInfo(self):
        qres = self.g.query('SELECT ?o ?p ?s WHERE {'
                                + '?o <http://openworm.org/entities/SimpleProperty/value> "motor". '
                                  '?o ?p ?s} ' #for that type ?o, get its value ?v
                                + 'LIMIT 10')
        for row in qres.result:
            print row

    def test_compare_to_xls(self):
        """ Compare the PyOpenWorm connections to the data in the spreadsheet """
        SAMPLE_CELL = 'ADAL'
        xls_conns = []
        pow_conns = []
        #
        qres = self.g.query("""SELECT ?pre_name ?post_name ?type (STR(?num) AS ?numval) WHERE {
                               ?conn a <http://openworm.org/entities/Connection>. #Grab all connections
                               #############################################################
                               # Go find the names for all cells on the "pre" side of the connection
                               #   and bind to ?pre_name
                               #############################################################
                               ?conn <http://openworm.org/entities/Connection/pre_cell> ?pre.
                               ?pre <http://openworm.org/entities/SimpleProperty/value> ?pre_cell.
                               ?pre_cell <http://openworm.org/entities/Cell/name> ?pre_namenode.
                               ?pre_namenode <http://openworm.org/entities/SimpleProperty/value> ?pre_name.

                               #############################################################
                               # Go find the names for all cells on the "post" side of the connection
                               #  and bind to ?post_name
                               #############################################################
                               ?conn <http://openworm.org/entities/Connection/post_cell> ?post.
                               ?post <http://openworm.org/entities/SimpleProperty/value> ?post_cell.
                               ?post_cell <http://openworm.org/entities/Cell/name> ?post_namenode.
                               ?post_namenode <http://openworm.org/entities/SimpleProperty/value> ?post_name.

                               ############################################################
                               # Go find the type of the connection and bind to ?type
                               #############################################################
                               ?conn <http://openworm.org/entities/Connection/syntype> ?syntype_node.
                               ?syntype_node <http://openworm.org/entities/SimpleProperty/value> ?type.

                               ############################################################
                               # Go find the number of the connection and bind to ?num
                               ############################################################
                               ?conn <http://openworm.org/entities/Connection/number> ?number_node.
                               ?number_node <http://openworm.org/entities/SimpleProperty/value> ?num.

                               ############################################################
                               # Filter by looking for the ?pre_name passed in
                               ############################################################
                               FILTER((isLiteral(?pre_name) && isLiteral(?post_name)) && (str(?pre_name) = \'"""
                               + SAMPLE_CELL + "\' || str(?post_name) = \'" + SAMPLE_CELL + "\'))}")
        def ff(x):
            return str(x.value)
        for line in qres.result:
            t = tuple(map(ff, line))
            pow_conns.append(t)
        #Get connections from the sheet 
        import xlrd
        wb = xlrd.open_workbook('OpenWormData/aux_data/NeuronConnect.xls')
        sheet = wb.sheets()[0]
        #Put every ADAL connection (except EMJs and Rs!) in a list as a tuple. This helps us compare them later
        def floatToStr(x):                  
            return str(int(x.value))        
        def sendOrGj(x):                    
            if x.value == 'EJ':             
                return 'gapJunction'        
            else:                           
                return 'send'               

        for row in range(1, sheet.nrows):
            if 'ADAL' in [sheet.cell(row, 0).value, sheet.cell(row, 1).value] and sheet.cell(row, 2).value in ['S', 'Sp', 'EJ']:
                string_row = [str(sheet.cell(row, 0).value), str(sheet.cell(row, 1).value), sendOrGj(sheet.cell(row, 2)), floatToStr(sheet.cell(row, 3))]
                t = tuple(string_row)
                xls_conns.append(t)
        #assert that these two sorted lists are the same
        #using sorted lists because Set() removes multiples
        self.assertTrue(sorted(pow_conns) == sorted(xls_conns))

@unittest.skipIf((TEST_CONFIG['rdf.source'] == 'Sleepycat') and (has_bsddb==False), "Sleepycat store will not work without bsddb")
class _DataTest(unittest.TestCase):
    TestConfig = TEST_CONFIG
    def delete_dir(self):
        self.path = self.TestConfig['rdf.store_conf']
        try:
            if self.TestConfig['rdf.source'] == "Sleepycat":
                subprocess.call("rm -rf "+self.path, shell=True)
            elif self.TestConfig['rdf.source'] == "ZODB":
                delete_zodb_data_store(self.path)
        except OSError, e:
            if e.errno == 2:
                # The file may not exist and that's fine
                pass
            else:
                raise e
    def setUp(self):
        # Set do_logging to True if you like walls of text
        td = '__tempdir__'
        z=self.TestConfig['rdf.store_conf']
        if z.startswith(td):
            x = z[len(td):]
            h=tempfile.mkdtemp()
            self.TestConfig['rdf.store_conf'] = h + x
        self.delete_dir()
        PyOpenWorm.connect(conf=self.TestConfig, do_logging=False)

    def tearDown(self):
        PyOpenWorm.disconnect()
        self.delete_dir()

    @property
    def config(self):
        return PyOpenWorm.config()

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
        with self.assertRaises(ValueError):
            Data.open("tests/bad_test.conf")

class ConfigureableTest(unittest.TestCase):
    def test_init_empty(self):
        """Ensure Configureable gets init'd with the defalut if nothing's given"""
        i = Configureable()
        self.assertEqual(Configureable.conf,i.conf)

    def test_init_False(self):
        """Ensure Configureable gets init'd with the defalut if False is given"""
        i = Configureable(conf=False)
        self.assertEqual(Configureable.conf, i.conf)

class CellTest(_DataTest):

    def test_DataUser(self):
        do = Cell('',conf=self.config)
        self.assertTrue(isinstance(do,DataUser))

    def test_lineageName(self):
        """ Test that we can retrieve the lineage name """
        c = Cell(name="ADAL",conf=self.config)
        c.lineageName("AB plapaaaapp")
        c.save()
        self.assertEqual("AB plapaaaapp", Cell(name="ADAL").lineageName())

    def test_same_name_same_id(self):
        """
        Test that two Cell objects with the same name have the same identifier()
        Saves us from having too many inserts of the same object.
        """
        c = Cell(name="boots")
        c1 = Cell(name="boots")
        self.assertEqual(c.identifier(),c1.identifier())

    def test_blast_space(self):
        """
        Test that setting the lineage name gives the blast cell.
        """
        c = Cell(name="carrots")
        c.lineageName("a tahsuetoahusenoatu")
        self.assertEqual(c.blast(), "a")

    def test_blast_dot(self):
        """
        Test that setting the lineage name gives the blast cell.
        """
        c = Cell(name="peas")
        c.lineageName("ab.tahsuetoahusenoatu")
        self.assertEqual(c.blast(), "ab")

    def test_parentOf(self):
        """
        Test that we can get the children of a cell
        Tests for anterior, posterior, left, right, ventral, dorsal divisions
        """
        p = Cell(name="peas")
        p.lineageName("ab.tahsuetoahusenoat")
        p.save()

        c = ["carrots",
             "jam",
             "peanuts",
             "celery",
             "tuna",
             "chicken"]

        division_directions = "alvpdr"

        for x,l in zip(c, division_directions):
            base = 'ab.tahsuetoahusenoat'
            ln = base + l
            Cell(name=x,lineageName=ln).save()

        names = set(str(x.name()) for x in p.parentOf())
        self.assertEqual(set(c), names)

    def test_daughterOf(self):
        """
        Test that we can get the parent of a cell
        """
        p = Cell(name="peas")
        p.lineageName("ab.tahsuetoahusenoat")
        p.save()

        c = Cell(name="carrots")
        c.lineageName("ab.tahsuetoahusenoatu")
        c.save()
        parent_p = c.daughterOf().name()
        self.assertEqual("peas", parent_p)

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
        self.config['rdf.graph'].parse("tests/PVDR.nml.rdf.xml",format='trig')
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

class DataObjectTestToo(unittest.TestCase):
    def test_helpful_message_on_non_connection(self):
        """ The message should say something about connecting """
        Configureable.conf = False # Ensure that we are disconnected
        with self.assertRaisesRegexp(Exception, ".*[cC]onnect.*"):
            do = DataObject()

class DataUserTest(_DataTest):

    def test_init_no_config(self):
        """ Should fail to initialize since it's lacking basic configuration """
        c = Configureable.conf
        Configureable.conf = False
        with self.assertRaises(BadConf):
            DataUser()
        Configureable.conf = c

    def test_init_no_config_with_default(self):
        """ Should suceed if the default configuration is a Data object """
        DataUser()

    def test_init_False_with_default(self):
        """ Should suceed if the default configuration is a Data object """
        DataUser(conf=False)

    def test_init_config_no_Data(self):
        """ Should fail if given a non-Data configuration """
        # XXX: This test touches some machinery in
        # PyOpenWorm/__init__.py. Feel like it's a bad test
        tmp = Configureable.conf
        Configureable.conf = Configure()
        with self.assertRaises(BadConf):
            DataUser()
        Configureable.conf = tmp
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

    def test_add_statements_completes(self):
        """ Test that we can upload lots of triples.

        This is to address the problem from issue #31 on https://github.com/openworm/PyOpenWorm/issues
        """
        g = rdflib.Graph()
        for i in range(9000):
            s = rdflib.URIRef("http://somehost.com/s%d" % i)
            p = rdflib.URIRef("http://somehost.com/p%d" % i)
            o = rdflib.URIRef("http://somehost.com/o%d" % i)
            g.add((s,p,o))
        du = DataUser(conf=self.config)
        du.add_statements(g)

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
        self.assertEqual('interneuron', self.neur('AVAL').type.one())

    def test_name(self):
        """ Test that the name property is set when the neuron is initialized with it """
        self.assertEqual('AVAL', self.neur('AVAL').name())
        self.assertEqual('AVAR', self.neur('AVAR').name())

    def test_neighbor(self):
        n = self.neur('AVAL')
        n.neighbor(self.neur('PVCL'))
        neighbors = list(n.neighbor())
        self.assertIn(self.neur('PVCL'), neighbors)
        n.save()
        self.assertIn(self.neur('PVCL'), list(self.neur('AVAL').neighbor()))

    def test_init_from_lineage_name(self):
        c = Neuron(lineageName="AB plapaaaap",name="ADAL")
        c.save()
        c = Neuron(lineageName="AB plapaaaap")
        self.assertEqual(c.name(), 'ADAL')

    def test_GJ_degree(self):
        """ Get the number of gap junctions from a networkx representation """
        # XXX: This test depends on a remote-hosted CSV file. Change it to depend
        # on the configured RDF graph, seeded by this test
        self.assertEqual(self.neur('AVAL').GJ_degree(),60)

    def test_Syn_degree(self):
        """ Get the number of chemical synapses from a networkx representation """
        # XXX: This test depends on a remote-hosted CSV file. Change it to depend
        # on the configured RDF graph, seeded by this test
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
        When multiple authors are on a paper, all of their names should be returned in an iterator. Publication order not necessarily preserved
        """
        pmid = "24098140"
        alist = [u"Frédéric MY","Lundin VF","Whiteside MD","Cueva JG","Tu DK","Kang SY","Singh H","Baillie DL","Hutter H","Goodman MB","Brinkman FS","Leroux MR"]
        self.assertEqual(set(alist), set(Evidence(pmid=pmid).author()))

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

    def test_asserts_query(self):
        """ Show that we can store the evidence on an object and later retrieve it """
        e = Evidence(author='tom@cn.com')
        r = Relationship(make_graph(10))
        e.asserts(r)
        e.save()
        e0 = Evidence()
        e0.asserts(r)
        s = list(e0.load())
        author = s[0].author.one()
        self.assertIn('tom@cn.com', author)

    def test_asserts_query_multiple(self):
        """ Show that setting the evidence with distinct objects yields distinct results """
        e = Evidence(author='tom@cn.com')
        r = Relationship(make_graph(10))
        e.asserts(r)
        e.save()

        e1 = Evidence(year=1999)
        e1.asserts(r)
        e1.save()

        e0 = Evidence()
        e0.asserts(r)
        for x in e0.load():
            a = x.author.one()
            y = x.year()
            # Testing that either a has a result tom@cn.com and y has nothing or
            # y has a result 1999 and a has nothing
            self.assertTrue((a == 'tom@cn.com' and y is None) or (a is None and int(y) == 1999))

    def test_asserts_query_multiple_author_matches(self):
        """ Show that setting the evidence with distinct objects yields distinct results even if there are matching values """
        e = Evidence(author='tom@cn.com')
        r = Relationship(make_graph(10))
        e.asserts(r)
        e.save()

        e1 = Evidence(author='tom@cn.com')
        e1.asserts(r)
        e1.save()

        e0 = Evidence()
        e0.asserts(r)
        self.assertTrue(len(list(e0.load())) == 2)

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
        """ Test that rdflib throws up a warning when we do something bad """
        #XXX: capture the logged warning
        import cStringIO
        import logging

        out = cStringIO.StringIO()
        logger = logging.getLogger()
        stream_handler = logging.StreamHandler(out)
        logger.addHandler(stream_handler)
        try:
            rdflib.URIRef("some random string")
        finally:
            logger.removeHandler(stream_handler)
        v = out.getvalue()
        out.close()
        self.assertRegexpMatches(str(v), r".*some random string.*")

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
        self.assertIsInstance(c.pre_cell(), Neuron)
        self.assertIsInstance(c.post_cell(), Neuron)
        self.assertEqual(c.number(), 3)
        self.assertEqual(c.syntype(), 'send')
        self.assertEqual(c.synclass(), 'Serotonin')

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

    def test_innervatedBy(self):
        m = Muscle('MDL08')
        n = Neuron('some neuron')
        m.innervatedBy(n)
        m.save()

        v = Muscle(name='MDL08')
        self.assertIn(Neuron('some neuron'), list(v.innervatedBy()))

    def test_muscle_neurons(self):
        """ Should be the same as innervatedBy """
        m = Muscle(name='MDL08')
        neu = Neuron(name="tnnetenba")
        m.neurons(neu)
        m.save()

        m = Muscle(name='MDL08')
        self.assertIn(Neuron('tnnetenba'), list(m.neurons()))

class DataTest(unittest.TestCase):
    def test_namespace_manager(self):
        c = Configure()
        c['rdf.source'] = 'default'
        c['rdf.store'] = 'default'
        Configureable.conf = c
        d = Data()
        d.openDatabase()

        self.assertIsInstance(d['rdf.namespace_manager'], R.namespace.NamespaceManager)

    def test_init_no_rdf_store(self):
        """ Should be able to init without these values """
        c = Configure()
        Configureable.conf = c
        d = Data()
        try:
            d.openDatabase()
        except:
            self.fail("Bad state")

    def test_ZODB_persistence(self):
        """ Should be able to init without these values """
        c = Configure()
        fname ='ZODB.fs'
        c['rdf.source'] = 'ZODB'
        c['rdf.store_conf'] = fname
        Configureable.conf = c
        d = Data()
        try:
            d.openDatabase()
            g = make_graph(20)
            for x in g:
                d['rdf.graph'].add(x)
            d.closeDatabase()

            d.openDatabase()
            self.assertEqual(20, len(list(d['rdf.graph'])))
            d.closeDatabase()
        except:
            traceback.print_exc()
            self.fail("Bad state")
        delete_zodb_data_store(fname)

    @unittest.skipIf((has_bsddb==False), "Sleepycat requires working bsddb")
    def test_Sleepycat_persistence(self):
        """ Should be able to init without these values """
        c = Configure()
        fname='Sleepycat_store'
        c['rdf.source'] = 'Sleepycat'
        c['rdf.store_conf'] = fname
        Configureable.conf = c
        d = Data()
        try:
            d.openDatabase()
            g = make_graph(20)
            for x in g:
                d['rdf.graph'].add(x)
            d.closeDatabase()

            d.openDatabase()
            self.assertEqual(20, len(list(d['rdf.graph'])))
            d.closeDatabase()
        except:
            traceback.print_exc()
            self.fail("Bad state")

        subprocess.call("rm -rf "+fname, shell=True)

    def test_trix_source(self):
        """ Test that we can load the datbase up from an XML file.
        """
        f = tempfile.mkstemp()

        c = Configure()
        c['rdf.source'] = 'trix'
        c['rdf.store'] = 'default'
        c['trix_location'] = f[1]

        with open(f[1],'w') as fo:
            fo.write(TD.TriX_data)

        connect(conf=c)
        c = config()

        try:
            g = c['rdf.graph']
            b = g.query("ASK { ?S ?P ?O }")
            for x in b:
                self.assertTrue(x)
        except ImportError:
            pass
        finally:
            disconnect()
        os.unlink(f[1])

    def test_trig_source(self):
        """ Test that we can load the datbase up from a trig file.
        """
        f = tempfile.mkstemp()

        c = Configure()
        c['rdf.source'] = 'serialization'
        c['rdf.serialization'] = f[1]
        c['rdf.serialization_format'] = 'trig'
        c['rdf.store'] = 'default'
        with open(f[1],'w') as fo:
            fo.write(TD.Trig_data)

        connect(conf=c)
        c = config()

        try:
            g = c['rdf.graph']
            b = g.query("ASK { ?S ?P ?O }")
            for x in b:
                self.assertTrue(x)
        except ImportError:
            pass
        finally:
            disconnect()

class PropertyTest(_DataTest):
    def test_one(self):
        """ `one` should return None if there isn't a value or just the value if there is one """
        class T(Property):
            def __init__(self):
                Property.__init__(self)
                self.b = False

            def get(self):
                if self.b:
                    yield "12"
        t = T()
        self.assertIsNone(t.one())
        t.b=True
        self.assertEqual('12', t.one())

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
        c = DataObject.DatatypeProperty("boots", do)
        c1 = DataObject.DatatypeProperty("boots", do1)
        self.assertEqual(c.identifier(),c1.identifier())

    def test_same_value_same_id_not_empty(self):
        """
        Test that two SimpleProperty with the same name have the same identifier()
        """
        do = DataObject(ident=R.URIRef("http://example.org"))
        do1 = DataObject(ident=R.URIRef("http://example.org"))
        c = DataObject.DatatypeProperty("boots", do)
        c1 = DataObject.DatatypeProperty("boots", do1)
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
        c = DataObject.ObjectProperty("boots", do)
        c1 = DataObject.ObjectProperty("boots", do1)
        do.boots(dz)
        do1.boots(dz1)
        self.assertEqual(c.identifier(),c1.identifier())

    def test_diff_value_diff_id_not_empty(self):
        """
        Test that two SimpleProperty with the same name have the same identifier()
        """
        do = DataObject(ident=R.URIRef("http://example.org"))
        do1 = DataObject(ident=R.URIRef("http://example.org"))
        c = DataObject.DatatypeProperty("boots", do)
        c1 = DataObject.DatatypeProperty("boots", do1)
        do.boots('join')
        do1.boots('partition')
        self.assertNotEqual(c.identifier(),c1.identifier())

    def test_diff_prop_same_name_same_object_same_value_same_id(self):
        """
        Test that two SimpleProperty with the same name have the same identifier()
        """
        # why would you ever do this?
        do = DataObject(ident=R.URIRef("http://example.org"))
        c = DataObject.DatatypeProperty("boots", do)
        c1 = DataObject.DatatypeProperty("boots", do)
        c('join')
        c1('join')
        self.assertEqual(c.identifier(),c1.identifier())

    def test_diff_prop_same_name_same_object_diff_value_same_id(self):
        """
        Test that two SimpleProperty with the same name have the same identifier()
        """
        # why would you ever do this?
        do = DataObject(ident=R.URIRef("http://example.org"))
        c = DataObject.DatatypeProperty("boots", do)
        c1 = DataObject.DatatypeProperty("boots", do)
        c('partition')
        c1('join')
        self.assertNotEqual(c.identifier(),c1.identifier())

    def test_diff_value_insert_order_same_id(self):
        """
        Test that two SimpleProperty with the same name have the same identifier()
        """
        do = DataObject(ident=R.URIRef("http://example.org"))
        do1 = DataObject(ident=R.URIRef("http://example.org"))
        c = DataObject.DatatypeProperty("boots", do)
        c1 = DataObject.DatatypeProperty("boots", do1)
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

        c = DataObject.ObjectProperty("boots", do)
        c1 = DataObject.ObjectProperty("boots", do1)

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
            owner_type = DataObject

        sp = T(owner=do)
        self.assertNotEqual(len(list(sp.triples())), 0)
        self.assertNotEqual(len(list(sp.triples(query=True))), 0)

class NeuroMLTest(_DataTest):
    pass

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-b", "--use-binary-database", dest="binary_db",
                      action="store_true", default=False,
                      help="Use the binary database for data integrity tests")

    (options, args) = parser.parse_args()
    USE_BINARY_DB = options.binary_db
    args = [sys.argv[0]] + args # We have to add back the first argument after parse_args
    unittest.main(argv=args)
