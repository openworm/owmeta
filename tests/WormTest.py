from __future__ import absolute_import
import rdflib as R
from .DataTestTemplate import _DataTest

from PyOpenWorm.worm import Worm
from PyOpenWorm.network import Network
from PyOpenWorm.muscle import Muscle


class WormTest(_DataTest):
    """Test for Worm."""
    ctx_classes = (Worm, Network, Muscle)

    def test_get_network(self):
        w = self.ctx.Worm()
        w.neuron_network(self.ctx.Network())
        self.save()
        nn = self.ctx.Worm().neuron_network()
        self.assertIsInstance(nn, Network)

    def test_muscles1(self):
        w = self.ctx.Worm()
        w.muscle(self.ctx.Muscle(name='MDL08'))
        w.muscle(self.ctx.Muscle(name='MDL15'))
        self.save()
        self.assertIn(self.ctx.Muscle(name='MDL08'), list(self.ctx.Worm().muscles()))
        self.assertIn(self.ctx.Muscle(name='MDL15'), list(self.ctx.Worm().muscles()))

    def test_get_semantic_net(self):
        g0 = self.ctx.Worm().get_semantic_net()
        self.assertTrue(isinstance(g0, R.ConjunctiveGraph))
