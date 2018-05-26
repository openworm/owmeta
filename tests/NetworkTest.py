from __future__ import absolute_import

import unittest

from PyOpenWorm.worm import Worm
from PyOpenWorm.network import Network
from PyOpenWorm.neuron import Neuron
from PyOpenWorm.connection import Connection
import networkx

from .DataTestTemplate import _DataTest


class NetworkTest(_DataTest):

    ctx_classes = (Worm, Network, Neuron)

    def setUp(self):
        super(NetworkTest, self).setUp()
        self.net = self.ctx.Network(conf=self.config)
        self.worm = self.ctx.Worm()
        self.worm.neuron_network(self.net)

    def test_aneuron(self):
        """
        Test that we can retrieve a Neuron by name.
        """
        self.assertTrue(isinstance(self.net.aneuron('AVAL'),
                                   Neuron))

    def test_neurons(self):
        """
        Test that we can add arbitrary Neurons to the Network,
        and that they can be accessed afterwards.
        """
        self.net.neuron(self.ctx.Neuron(name='AVAL'))
        self.net.neuron(self.ctx.Neuron(name='DD5'))
        self.save()

        nns = set(self.net.neuron_names())
        self.assertTrue('AVAL' in nns)
        self.assertTrue('DD5' in nns)

    def test_synapses_rdf(self):
        """ Check that synapses() returns connection objects """
        for x in self.net.synapse():
            self.assertIsInstance(x, Connection)
            break

    @unittest.skip('not implemented')
    def test_as_networkx(self):
        """Test that as_networkx returns the correct type."""
        self.assertTrue(isinstance(self.net.as_networkx(), networkx.DiGraph))

    def test_interneurons(self):
        n0 = self.ctx.Neuron(name='TestNeuron0')
        n1 = self.ctx.Neuron(name='TestNeuron1')
        n1.type('interneuron')
        self.net.neuron(n0)
        self.net.neuron(n1)
        self.save()
        n = self.context.stored(Network)()
        self.assertIn(n1, n.interneurons())
