from __future__ import print_function
from __future__ import absolute_import

from .DataTestTemplate import _DataTest

from PyOpenWorm.muscle import Muscle
from PyOpenWorm.neuron import Neuron


class MuscleTest(_DataTest):
    ctx_classes = (Muscle, Neuron)

    def test_muscle(self):
        self.assertTrue(isinstance(Muscle(name='MDL08'), Muscle))

    def test_innervatedBy(self):
        m = self.ctx.Muscle('MDL08')
        n = self.ctx.Neuron('some neuron')
        m.innervatedBy(n)
        self.save()
        v = self.ctx.Muscle(name='MDL08')
        self.assertIn(n, list(v.innervatedBy()))

    def test_muscle_neurons(self):
        """ Should be the same as innervatedBy """
        m = self.ctx.Muscle(name='MDL08')
        neu = self.ctx.Neuron(name="tnnetenba")
        m.neurons(neu)
        self.save()

        m = self.ctx.Muscle(name='MDL08')
        self.assertIn(self.ctx.Neuron('tnnetenba'), list(m.neurons()))
