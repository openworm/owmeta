from __future__ import absolute_import
from owmeta.connection import Connection
from owmeta.neuron import Neuron
import rdflib as R

from .DataTestTemplate import _DataTest


class ConnectionTest(_DataTest):
    ctx_classes = (Connection,)

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
        c = Connection(Neuron(name='AVAL'), Neuron(name='ADAR'), 3, 'send', 'Serotonin')
        self.assertIsInstance(c.pre_cell(), Neuron)
        self.assertIsInstance(c.post_cell(), Neuron)
        self.assertEqual(c.number(), 3)
        self.assertEqual(c.syntype(), 'send')
        self.assertEqual(c.synclass(), 'Serotonin')

    def test_init_number_is_a_number(self):
        with self.assertRaises(Exception):
            Connection(1, 2, "gazillion", 4, 5)

    def test_init_with_neuron_objects(self):
        n1 = Neuron(name="AVAL")
        n2 = Neuron(name="PVCR")
        try:
            Connection(n1, n2)
        except Exception:
            self.fail("Shouldn't fail on Connection init")

    def test_load1(self):
        """ Put the appropriate triples in. Try to load them """
        g = R.ConjunctiveGraph()
        self.config['rdf.graph'] = g
        for t in self.trips:
            g.add(t)
        c = self.ctx.Connection(conf=self.config)
        for x in c.load():
            self.assertIsInstance(x, Connection)

    def test_load_with_filter(self):
        # Put the appropriate triples in. Try to load them
        g = R.ConjunctiveGraph()
        self.config['rdf.graph'] = g
        for t in self.trips:
            g.add(t)
        c = Connection(pre_cell=Neuron(name="PVCR"), conf=self.config)
        r = c.load()
        for x in r:
            self.assertIsInstance(x, Connection)
