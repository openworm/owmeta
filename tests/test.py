from __future__ import absolute_import
from __future__ import print_function
# -*- coding: utf-8 -*-

import sys
from six.moves import range
from six.moves import zip
sys.path.insert(0,".")
import unittest
import neuroml
import neuroml.writers as writers
import PyOpenWorm
from PyOpenWorm import *
import networkx
import rdflib
import rdflib as R
import pint as Q
import os
import subprocess as SP
import subprocess
import tempfile
import doctest

from glob import glob

USE_BINARY_DB = False
BINARY_DB = "OpenWormData/worm.db"
TEST_CONFIG = "tests/default_test.conf"
try:
    import bsddb
    has_bsddb = True
except ImportError:
    has_bsddb = False

try:
    import numpy
    has_numpy = True
except ImportError:
    has_numpy = False

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

def delete_zodb_data_store(path):
    os.unlink(path)
    os.unlink(path + '.index')
    os.unlink(path + '.tmp')
    os.unlink(path + '.lock')


# Tests for the Configure class, which provides functionality to modules to
# allow outside objects to parameterize their behavior
from .ConfigureTest import ConfigureTest

# Integration tests that read from the database and ensure that basic queries
# have expected answers, as a way to keep data quality high.
from .DataIntegrityTest import DataIntegrityTest

# Integration tests that ensure basic functioning of the database backend and
# connection
from .DatabaseBackendTest import DatabaseBackendTest

# Runs the examples to make sure we didn't break the API for them.
from .ExampleRunnerTest import ExampleRunnerTest

# Tests our Quantity class, which is used for defining things with measurement
# units
from .QuantityTest import QuantityTest

# Tests RDFLib, our backend library that interfaces with the database as an
# RDF graph.
from .RDFLibTest import RDFLibTest


class _DataTest(unittest.TestCase):
    def delete_dir(self):
        self.path = self.TestConfig['rdf.store_conf']
        try:
            if self.TestConfig['rdf.source'] == "Sleepycat":
                subprocess.call("rm -rf "+self.path, shell=True)
            elif self.TestConfig['rdf.source'] == "ZODB":
                delete_zodb_data_store(self.path)
        except OSError as e:
            if e.errno == 2:
                # The file may not exist and that's fine
                pass
            else:
                raise e
    def setUp(self):
        # Set do_logging to True if you like walls of text
        self.TestConfig = Configure.open(TEST_CONFIG)
        td = '__tempdir__'
        z = self.TestConfig['rdf.store_conf']
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
        base = 'ab.tahsuetoahusenoat'
        p.lineageName(base)
        p.save()

        c = ["carrots",
             "jam",
             "peanuts",
             "celery",
             "tuna",
             "chicken"]

        division_directions = "alvpdr"

        for x,l in zip(c, division_directions):
            ln = base + l
            Cell(name=x,lineageName=ln).save()
        names = set(str(x.name()) for x in p.parentOf())
        self.assertEqual(set(c), names)

    def test_daughterOf(self):
        """
        Test that we can get the parent of a cell
        """
        base = "ab.tahsuetoahusenoat"
        child = base + "u"
        p = Cell(name="peas")
        p.lineageName(base)
        p.save()

        c = Cell(name="carrots")
        c.lineageName(child)
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
        self.config['rdf.graph'].parse("tests/test_data/PVDR.nml.rdf.xml",format='trig')
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
        except Exception as e:
            print(e)
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
        except Exception as e:
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


class NetworkTest(_DataTest):
    def setUp(s):
        _DataTest.setUp(s)
        s.net = Network(conf=s.config)

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
        """ Show that setting the evidence with distinct objects yields
            distinct results """
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
            self.assertTrue(a == 'tom@cn.com' and int(y) == 1999)

    def test_asserts_query_multiple_author_matches(self):
        """ Show that setting the evidence with distinct objects yields
        distinct results even if there are matching values """
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
        self.assertEqual(len(list(sp.triples())), 0)
        self.assertEqual(len(list(sp.triples(query=True))), 0)

class NeuroMLTest(_DataTest):
    pass


# Tests from README.md
class DocumentationTest(unittest.TestCase):
    def test_readme(self):
        [failure_count, return_count] = doctest.testfile("../README.md")
        self.assertEqual(failure_count, 0)

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-b", "--use-binary-database", dest="binary_db",
                      action="store_true", default=False,
                      help="Use the binary database for data integrity tests")

    (options, args) = parser.parse_args()
    USE_BINARY_DB = options.binary_db

    def getTests(testCase):
        return unittest.TestLoader().loadTestsFromTestCase(testCase)

    def runTests(suite):
        return unittest.TextTestRunner().run(suite)

    all_tests = []
    configs = glob("tests/test_*.conf")
    if not has_bsddb:
        configs = [x for x in configs if 'Sleepycat' not in x]
    print("Testing with configs:",configs)
    for x in configs:
        TEST_CONFIG = x
        suite = unittest.TestSuite()
        suite.addTests(getTests(x) for x in _DataTest.__subclasses__())
        all_tests.append(suite)

    suite = unittest.TestSuite()
    classes = [x for x in list(globals().values()) if isinstance(x, type)]
    non_DataTestTests = (x for x in classes if (issubclass(x, unittest.TestCase) and not issubclass(x,  _DataTest)))
    suite.addTests(getTests(x) for x in non_DataTestTests)
    all_tests.append(suite)

    all_tests_flattened = []
    for x in all_tests:
        for y in x:
            for z in y:
                all_tests_flattened.append(z)

    suite = unittest.TestSuite()
    if len(args) == 1:
        suite.addTests([x for x in all_tests_flattened if x.id().startswith("__main__."+args[0])])
    else:
        suite.addTests(all_tests)

    res = runTests(suite)
    sys.exit(len(res.failures + res.errors)>0)
