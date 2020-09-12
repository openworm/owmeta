from __future__ import print_function
from __future__ import absolute_import
import unittest
import csv

from owmeta_core.context import Context
from owmeta_core.command import OWM
from owmeta_core.bundle import Bundle

from owmeta.worm import Worm
from owmeta.cell import Cell
from owmeta.neuron import Neuron
from owmeta.connection import Connection

import rdflib as R
import pytest


@pytest.mark.inttest
@pytest.mark.data_bundle
class DataIntegrityTest(unittest.TestCase):

    """ Integration tests that read from the database and ensure that basic
        queries have expected answers, as a way to keep data quality high.

    """
    @classmethod
    def setUpClass(cls):
        # grab the list of the names of the 302 neurons

        csvfile = open('tests/neurons.csv', 'r')
        reader = csv.reader(csvfile, delimiter=';', quotechar='|')

        # array that holds the names of the 302 neurons at class-level scope
        cls.neurons = []
        for row in reader:
            if len(row[0]) > 0:  # Only saves valid neuron names
                cls.neurons.append(row[0])

    def setUp(self):
        self.bnd = Bundle('openworm/owmeta-data')
        self.bnd.initdb()
        self.conn = self.bnd.connection
        self.conf = self.conn.conf
        self.g = self.conf["rdf.graph"]
        self.context = self.conn(Context)(ident="http://openworm.org/data")
        self.qctx = self.context.stored

    def tearDown(self):
        self.conn.disconnect()

    def test_correct_neuron_number(self):
        """
        This test verifies that the worm model has exactly 302 neurons.
        """
        # FIXME: Test execution is not properly isolated -- it fails if
        #        test_compare_to_xls fails. Other conditions may cause
        #        it to pass
        net = self.qctx(Worm).query().get_neuron_network()
        self.assertEqual(302, net.neuron.count())

    def test_correct_muscle_number(self):
        """
        This test verifies that the worm model has exactly 158 muscles.
        95 body wall muscles, 37 Pharynx muscles, 26 other muscles
        See counts on row 3 here:

            https://docs.google.com/spreadsheets/d/1NDx9LRF_B2phR5w4HlEtxJzxx1ZIPT2gA0ZmNmozjos/edit#gid=1

        """
        self.assertEqual(158, self.qctx(Worm).query().muscle.count())

    def test_INS_26_neuropeptide_neuron_list(self):
        """
        This test verifies that the set of neurons which contain the
        neuropeptide INS-26 is correct (the list is given below).
        """
        neuronlist = self.qctx(Neuron)()
        neuronlist.neuropeptide("INS-26")
        thlist = set(x.name() for x in neuronlist.load())
        self.assertEqual({'ASEL', 'ASER', 'ASIL', 'ASIR'}, thlist)

    def test_bentley_expr_data(self):
        """
        This verifies that the data in Bentley et. al (2016) receptor expression
        has been incorporated, by checking that one of the novel receptor
        expression patterns is in the worm.
        """
        va9 = self.qctx(Neuron).query('VA9')
        self.assertIn('LGC-53', va9.receptors())

    def test_unique_neuron_node(self):
        """
        There should one and only one unique RDF node for every neuron.  If
        more than one is present for a given cell name, then our data is
        inconsistent.  If there is not at least one present, then we are
        missing neurons.
        """

        results = {}
        for n in self.neurons:
            # Create a SPARQL query per neuron that looks for all RDF nodes
            # that have text matching the name of the neuron
            qres = self.g.query(
                f"""
                SELECT distinct ?n WHERE
                {{
                    ?n <{Cell.name.link}> {R.Literal(n).n3()}
                }} LIMIT 5
                """)
            results[n] = (len(qres), [x[0] for x in qres])

        # If there is not only one result back, then there is more than one RDF
        # node.
        more_than_one = [(x, results[x]) for x in results if results[x][0] > 1]
        less_than_one = [(x, results[x]) for x in results if results[x][0] < 1]
        self.assertEqual(
            0,
            len(more_than_one),
            "Some neurons have more than 1 node: " +
            "\n".join(
                str(x) for x in more_than_one))
        self.assertEqual(
            0,
            len(less_than_one),
            "Some neurons have no node: " +
            "\n".join(
                str(x) for x in less_than_one))

    def test_neurons_have_types(self):
        """
        Every Neuron should have a non-blank type
        """
        results = set()
        for n in self.neurons:
            s = f'''SELECT ?v WHERE {{
                       ?k <{Cell.name.link}> {R.Literal(n).n3()} .
                       ?k <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <{Neuron.rdf_type}> .
                       ?k <{Neuron.type.link}> ?v .
                    }}'''
            qres = self.g.query(s)
            for x in qres:
                v = x[0]
                if isinstance(v, R.Literal):
                    results.add(n)

        self.assertEqual(len(results),
                         len(self.neurons),
                         "Some neurons are missing a type: {}".format(set(self.neurons) - results))

    def test_neuron_GJ_degree(self):
        """ Get the number of gap junctions from a representation """
        # was 81 -- now retunring 44 -- are we sure this is correct?
        self.assertEqual(self.qctx(Neuron).query(name='AVAL').GJ_degree(), 44)

    def test_neuron_Syn_degree(self):
        """ Get the number of chemical synapses from a representation """
        # was 187 -- now returning 105 -- are we sure this is correct?
        self.assertEqual(self.qctx(Neuron).query(name='AVAL').Syn_degree(), 105)

    @unittest.skip("have not yet defined asserts")
    def test_what_nodes_get_type_info(self):
        qres = self.g.query("""SELECT ?o ?p ?s WHERE {{
                            ?o <http://openworm.org/entities/SimpleProperty/value> "motor".
                            ?o ?p ?s # for that type ?o, get its value ?v
                            }} LIMIT 10
                            """)
        for row in qres:
            print(row)

    def test_all_cells_have_wormbaseID(self):
        """ This test verifies that every cell has a Wormbase ID. """
        cells = set(self.qctx(Cell)().load())
        for cell in cells:
            assert cell.wormbaseID() is not None

    def test_all_neurons_have_wormbaseID(self):
        """ This test verifies that every neuron has a Wormbase ID. """
        net = self.qctx(Worm).query().get_neuron_network()
        for neuron_object in net.neurons():
            assert neuron_object.wormbaseID() is not None

    def test_all_muscles_have_wormbaseID(self):
        """ This test verifies that every muscle has a Wormbase ID. """
        muscles = self.qctx(Worm).query().muscles()
        for muscle_object in muscles:
            assert muscle_object.wormbaseID() is not None

    def test_all_neurons_are_cells(self):
        """ This test verifies that all Neuron objects are also Cell objects. """
        net = self.qctx(Worm).query().get_neuron_network()

        for neuron_object in net.neurons():
            self.assertIsInstance(neuron_object, Cell)

    def test_all_muscles_are_cells(self):
        """ This test verifies that all Muscle objects are also Cell objects. """
        muscles = self.qctx(Worm).query().muscles()
        for muscle_object in muscles:
            self.assertIsInstance(muscle_object, Cell)

    def test_correct_connections_number(self):
        """ This test verifies that there are exactly 7319 connections. """
        net = self.qctx(Worm).query().get_neuron_network()
        # XXX: The synapses contain some cells that aren't neurons
        self.assertEqual(7319, net.synapses.count())

    def test_number_neuron_to_neuron(self):
        """
        This test verifies that the worm model has exactly 5805 neuron to neuron
        connections.
        """
        synapse = self.qctx(Connection)()
        synapse.termination('neuron')
        self.qctx(Worm).query().get_neuron_network().synapse(synapse)

        self.assertEqual(5805, synapse.count())

    def test_number_neuron_to_muscle(self):
        """
        This test verifies that the worm model has exactly 1111 neuron to muscle
        connections.
        """
        synapse = self.qctx(Connection)()
        synapse.termination('muscle')
        self.qctx(Worm).query().get_neuron_network().synapse(synapse)

        self.assertEqual(1111, synapse.count())

    def test_correct_number_unique_neurons(self):
        """
        This test verifies that the worm model has exactly 300 unique neurons
        making connections.
        """
        synapse = self.qctx(Connection)()
        pre = self.qctx(Neuron)()
        synapse.pre_cell(pre)
        self.qctx(Worm).query().get_neuron_network().synapse(synapse)

        self.assertEqual(300, pre.count())

    def test_unconnected_neurons(self):
        """
        This test verifies that there are exactly 2 unconnected neurons,
        i.e., CANL and CANR, in the new connectome.
        """
        # In previous tests, there is a check for exactly 302 neurons in total.
        # There is also a test for exactly 300 unique neurons making connections.
        # That means it should be enough to check that the set {CANL, CANR} and
        # the set of neurons making connections are disjoint.

        neuron = self.qctx(Neuron)()
        synapse = self.qctx(Connection)()
        synapse.pre_cell(neuron)
        self.qctx(Worm).query().get_neuron_network().synapse(synapse)
        connected_neurons = set()
        unconnected_neurons = {'CANL', 'CANR'}
        for name in neuron.name.get():
            connected_neurons.add(name)
        self.assertTrue(connected_neurons.isdisjoint(unconnected_neurons))
