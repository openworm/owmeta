from __future__ import print_function
from __future__ import absolute_import

from PyOpenWorm.muscle import Muscle
from PyOpenWorm.neuron import Neuron

from .DataTestTemplate import _DataTest


class MuscleTest(_DataTest):

    def test_muscle(self):
        self.assertTrue(isinstance(Muscle(name='MDL08'), Muscle))

    def test_innervatedBy(self):
        m = Muscle('MDL08')
        n = Neuron('some neuron')
        m.innervatedBy(n)
        m.save()
        v = Muscle(name='MDL08')
        self.assertIn(n, list(v.innervatedBy()))

    def test_muscle_neurons(self):
        """ Should be the same as innervatedBy """
        m = Muscle(name='MDL08')
        neu = Neuron(name="tnnetenba")
        m.neurons(neu)
        m.save()

        m = Muscle(name='MDL08')
        self.assertIn(Neuron('tnnetenba'), list(m.neurons()))
