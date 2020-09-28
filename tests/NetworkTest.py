from __future__ import absolute_import
from owmeta.worm import Worm
from owmeta.network import Network
from owmeta.neuron import Neuron
from owmeta.connection import Connection

from .DataTestTemplate import _DataTest


class NetworkTest(_DataTest):

    ctx_classes = (Worm, Network, Neuron)

    def setUp(self):
        super(NetworkTest, self).setUp()
        self.net = self.ctx.Network(conf=self.TestConfig)
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
        net = self.ctx.Network()
        nns = set(net.neuron_names())
        self.assertTrue('AVAL' in nns)
        self.assertTrue('DD5' in nns)

    def test_synapses_rdf(self):
        """ Check that synapses() returns connection objects """
        for x in self.net.synapse():
            self.assertIsInstance(x, Connection)
            break

    def test_interneurons(self):
        n0 = self.ctx.Neuron(name='TestNeuron0')
        n1 = self.ctx.Neuron(name='TestNeuron1')
        n1.type('interneuron')
        self.net.neuron(n0)
        self.net.neuron(n1)
        self.save()
        n = self.context.stored(Network)()
        self.assertIn(n1.identifier, [x.identifier for x in n.interneurons()])
