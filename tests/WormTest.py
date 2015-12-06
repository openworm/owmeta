import sys
import rdflib as R

sys.path.insert(0,".")
#from PyOpenWorm import *
from PyOpenWorm.worm import Worm
from PyOpenWorm.network import Network
from PyOpenWorm.muscle import Muscle


from DataTestTemplate import _DataTest

class WormTest(_DataTest):
    """Test for Worm."""
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
        self.assertTrue(isinstance(g0, R.ConjunctiveGraph))
