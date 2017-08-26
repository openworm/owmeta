from __future__ import absolute_import
import sys
sys.path.insert(0, ".")
import PyOpenWorm
from PyOpenWorm import Worm, Network, Neuron, Connection
import networkx

from .DataTestTemplate import _DataTest


class NetworkTest(_DataTest):

    def setUp(s):
        _DataTest.setUp(s)
        s.net = Network(conf=s.config)
        s.worm = Worm()
        s.worm.neuron_network(s.net)

    def test_aneuron(self):
        """
        Test that we can retrieve a Neuron by name.
        """
        self.assertTrue(isinstance(self.net.aneuron('AVAL'),
                        PyOpenWorm.Neuron))

    def test_neurons(self):
        """
        Test that we can add arbitrary Neurons to the Network,
        and that they can be accessed afterwards.
        """
        self.net.neuron(Neuron(name='AVAL'))
        self.net.neuron(Neuron(name='DD5'))
        self.net.save()

        self.assertTrue('AVAL' in self.net.neuron_names())
        self.assertTrue('DD5' in self.net.neuron_names())

    def test_synapses_rdf(self):
        """ Check that synapses() returns connection objects """
        for x in self.net.synapse():
            self.assertIsInstance(x, Connection)
            break

    def test_as_networkx(self):
        """Test that as_networkx returns the correct type."""
        self.assertTrue(isinstance(self.net.as_networkx(), networkx.DiGraph))
