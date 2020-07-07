from __future__ import absolute_import
import rdflib as R
from .DataTestTemplate import _DataTest

from owmeta.worm import Worm
from owmeta.network import Network
from owmeta.muscle import Muscle


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
        self.assertIn(self.ctx.Muscle(name='MDL08').identifier,
                      self.ctx.Worm().muscle.get_terms())
        self.assertIn(self.ctx.Muscle(name='MDL15').identifier,
                      self.ctx.Worm().muscle.get_terms())

    def test_get_semantic_net(self):
        g0 = self.ctx.Worm().get_semantic_net()
        self.assertTrue(isinstance(g0, R.ConjunctiveGraph))
