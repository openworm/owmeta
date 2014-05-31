import unittest

import PyOpenWorm
import subprocess
from PyOpenWorm import Configure,ConfigValue,Network,Worm,Neuron,Data,DataUser
import networkx
import rdflib
import rdflib as R

def setup(self):
    c = Configure()
    c['connectomecsv'] = 'https://raw.github.com/openworm/data-viz/master/HivePlots/connectome.csv'
    c['neuronscsv'] = 'https://raw.github.com/openworm/data-viz/master/HivePlots/neurons.csv'
    c['sqldb'] = '/home/markw/work/openworm/PyOpenWorm/db/celegans.db'
    #c['rdf.source'] = 'sqlite'
    c['rdf.source'] = 'sparql_endpoint'
    c['rdf.store_conf'] = ('http://107.170.133.175:8080/openrdf-sesame/repositories/test','http://107.170.133.175:8080/openrdf-sesame/repositories/test/statements')
    self.config = Data(c)
    self.config['user.email'] = 'jerry@cn.com'
    self.config_no_data = c

class PyOpenWormTest(unittest.TestCase):
    """Test for PyOpenWorm."""

    @classmethod
    def setUpClass(cls):
        # XXX: clear the database and reload it from the schema and default data files
        pass
    def setUp(self):
        setup(self)

    def test_worm_get_network(self):
        self.assertTrue(isinstance(PyOpenWorm.Worm(self.config).get_neuron_network(), PyOpenWorm.Network))

    def test_worm_get_semantic_net(self):
        g0 = PyOpenWorm.Worm(self.config).get_semantic_net()
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

    def test_neuron_get_reference(self):
        self.assertIn('http://dx.doi.org/10.100.123/natneuro', PyOpenWorm.Neuron('ADER',self.config).get_reference('Receptor','EXP-1'))
        self.assertEqual(PyOpenWorm.Neuron('ADER',self.config).get_reference('Receptor','DOP-2'), [])

    def test_neuron_add_reference(self):
        e = self.config
        PyOpenWorm.Neuron('ADER', e).add_reference('Receptor', 'EXP-1', pmid='some_pmid')
        self.assertIn('some_pmid', PyOpenWorm.Neuron('ADER',e).get_reference('Receptor','EXP-1'))

    def test_neuron_add_statements(self):
        # generate random statements
        g = rdflib.Graph()
        for i in range(1000):
            s = rdflib.URIRef("http://somehost.com/s%d" % i)
            p = rdflib.URIRef("http://somehost.com/p%d" % i)
            o = rdflib.URIRef("http://somehost.com/o%d" % i)
            g.add((s,p,o))
        PyOpenWorm.Neuron('ADER', self.config).add_statements(g)

    @unittest.skip("Long runner")
    def test_neuron_persistence(self):
        d = Configure(self.config_no_data)
        d['rdf.store'] = 'Sleepycat'
        d['rdf.store_conf'] = 'tests/test.bdb'
        e = Data(d)

        PyOpenWorm.Neuron('ADER', e).add_reference('Receptor', 'EXP-1', pmid='some_pmid')
        self.assertIn('some_pmid', PyOpenWorm.Neuron('ADER',e).get_reference(0,'EXP-1'))

        e = Data(d)

        self.assertIn('some_pmid', PyOpenWorm.Neuron('ADER',e).get_reference(0,'EXP-1'))

        assert('some_pmid' not in PyOpenWorm.Neuron('ADER',self.config).get_reference(0,'EXP-1'))
        subprocess.call('rm -rf tests/test.bdb')

    def test_muscle(self):
        self.assertTrue(isinstance(PyOpenWorm.Muscle('MDL08',self.config),PyOpenWorm.Muscle))

    def test_muscle_neurons(self):
        m = PyOpenWorm.Muscle('MDL08',self.config).neurons()
        for k in m:
            print k

class ConfigureTest(unittest.TestCase):
    def test_fake_config(self):
        with self.assertRaises(KeyError):
            c = Configure()
            k = c['not_a_valid_config']

    def test_configure_literal(self):
        c = Configure()
        c['seven'] = "coke"
        self.assertEqual(c['seven'], "coke")

    def test_configure_getter(self):
        c = Configure()
        class pipe(ConfigValue):
            def get(self):
                return "sign"
        c['seven'] = pipe()
        self.assertEqual(c['seven'], "sign")

    def test_configure_late_get(self):
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

class CellTest(unittest.TestCase):
    def setUp(s):
        setup(s)

    def test_DataUser(self):
        do = Cell()
        self.assertTrue(isinstance(do,PyOpenWorm.DataUser))
    def test_lineageName(self):
        c = Cell(name="ADAL")
        self.assertEqual(c.lineageName(), ["AB plapaaaapp"])

class DataObjectTest(unittest.TestCase):
    def setUp(s):
        setup(s)

    def test_DataUser(self):
        do = DataObject()
        self.assertTrue(isinstance(do,PyOpenWorm.DataUser))
    def test_identifier(self):
        do = DataObject(ident="http://example.org")
        self.assertEqual(do.identifier(), R.URIRef("http://example.org"))

    def test_identifier(self):
        do = DataObject(ident="http://example.org")
        self.assertEqual(do.identifier(), R.URIRef("http://example.org"))

class NeuronTest(unittest.TestCase):
    def setUp(s):
        setup(s)
        s.neur = lambda x : Neuron(x,s.config)

    def test_Cell(self):
        do = Neuron('BDUL')
        self.assertTrue(isinstance(do,Cell))

    def test_identifier(self):
        g = self.config['rdf.graph']
        q = "PREFIX ns1:<http://openworm.org/entities/> select ?x where { ?z rdfs:label ?x . ?z ns1:1515 ns1:1 }"
        neurons = [r['x'] for r in g.query(q)]
        for x in neurons:
            t = g.query('select ?x where { ?x rdfs:label "%s" }' % str(x))
            for m in t:
                print "testing "+str(x)
                ident = self.neur(x).identifier()
                self.assertEqual(m, ident)

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

    def test_GJ_degree(self):
        self.assertEqual(self.neur('AVAL').GJ_degree(),60)

    def test_Syn_degree(self):
        self.assertEqual(self.neur('AVAL').Syn_degree(),74)

class NetworkTest(unittest.TestCase):
    def setUp(s):
        setup(s)
        s.net = Network(s.config)

    def test_identifier(s):
        ident = self.net.identifier()
        self.assertEqual(self.config['rdf.namespace']["worm_net"], ident)

    def test_network(self):
        self.assertTrue(isinstance(self.net,Network))

    def test_network_aneuron(self):
        self.assertTrue(isinstance(self.net.aneuron('AVAL'),PyOpenWorm.Neuron))

    def test_network_neurons(self):
        self.assertTrue('AVAL' in self.net.neurons())
        self.assertTrue('DD5' in self.net.neurons())
        self.assertEqual(len(list(self.net.neurons())), 302)

    def test_worm_muscles(self):
        self.assertTrue('MDL08' in PyOpenWorm.Worm(self.config).muscles())
        self.assertTrue('MDL15' in PyOpenWorm.Worm(self.config).muscles())

    def test_network_as_networkx(self):
        self.assertTrue(isinstance(self.net.as_networkx(),networkx.DiGraph))

class EvidenceTest(unittest.TestCase):
    def setUp(s):
        setup(s)

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
    def test_reification(self):
        graph = R.Graph(store="SPARQLUpdateStore")
        graph.open(("http://localhost:8080/openrdf-sesame/repositories/test","http://localhost:8080/openrdf-sesame/repositories/test/statements"))
        update_stmt = "INSERT DATA { _:stmt ns1:subject ns1:a ; ns1:predicate ns1:b ; ns1:object ns1:c . _:someone ns1:says _:stmt }"
        for i in range(3):
            graph.update(update_stmt, initNs=self.ns)
        r = graph.query("select ?z { ?p ns1:subject ?x . ?z ns1:says ?p }", initNs=self.ns)
        for k in r:
            print k

class TimeTest(unittest.TestCase):
    def test_datetime_isoformat_has_timezone(self):
        import pytz
        from datetime import datetime as DT
        time_stamp = DT.now(pytz.utc).isoformat()
        self.assertRegexpMatches(time_stamp, r'.*[+-][0-9][0-9]:[0-9][0-9]$')
