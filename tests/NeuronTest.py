from __future__ import print_function
from __future__ import absolute_import

from .DataTestTemplate import _DataTest

from PyOpenWorm.neuron import Neuron
from PyOpenWorm.cell import Cell
from PyOpenWorm.connection import Connection
from PyOpenWorm.context import Context


class NeuronTest(_DataTest):
    ctx_classes = (Neuron, Connection)

    def setUp(self):
        _DataTest.setUp(self)
        self.neur = lambda x: self.ctx.Neuron(name=x)

    def test_Cell(self):
        do = self.neur('BDUL')
        self.assertTrue(isinstance(do, Cell))

    def test_receptors(self):
        n = self.neur('AVAL')
        n.receptor('GLR-2')
        self.save()
        self.assertIn('GLR-2', list(self.neur('AVAL').receptors()))

    def test_same_name_same_id(self):
        """
        Test that two Neuron objects with the same name have the same
        identifier. Saves us from having too many inserts of the same object.
        """
        c = Neuron(name="boots")
        c1 = Neuron(name="boots")
        self.assertEqual(c.identifier, c1.identifier)

    def test_type(self):
        n = self.neur('AVAL')
        n.type('interneuron')
        self.save()
        self.assertEqual('interneuron', self.neur('AVAL').type.one())

    def test_name(self):
        """
        Test that the name property is set when the neuron is initialized
        with it
        """
        self.assertEqual('AVAL', self.neur('AVAL').name())
        self.assertEqual('AVAR', self.neur('AVAR').name())

    def test_neighbor(self):
        n = self.neur('AVAL')
        n.neighbor(self.neur('PVCL'), syntype='send')
        neighbors = list(n.neighbor())
        self.assertIn(self.neur('PVCL'), neighbors)
        self.save()
        self.assertIn(self.neur('PVCL'), list(self.neur('AVAL').neighbor()))

    def test_neighbor_count(self):
        n = self.neur('AVAL')
        n.neighbor(self.neur('PVCL'), syntype='send')
        self.save()
        p = self.ctx.Neuron()
        self.neur('AVAL').neighbor(p)
        self.assertEqual(1, p.count())

    def test_neighbor_count_staged(self):
        n = self.neur('AVAL')
        n.neighbor(self.neur('PVCL'), syntype='send')
        self.assertEqual(1, n.neighbor.count())

    def test_neighbor_count_context_staged(self):
        n = self.neur('AVAL')
        n.neighbor(self.neur('PVCL'), syntype='send')
        ctx1 = Context(ident='http://example.org/ctx1')
        self.assertEqual(0, ctx1(n).neighbor.count())

    def test_connection_count(self):
        n = self.neur('AVAL')
        n.connection(self.ctx.Connection(n, self.neur('PVCL'), syntype='send'))
        self.save()
        self.assertEqual(1, self.neur('AVAL').connection.count())

    def test_connection_count_staged(self):
        n = self.neur('AVAL')
        n.connection(self.ctx.Connection(n, self.neur('PVCL'), syntype='send'))
        self.assertEqual(1, n.connection.count())

    def test_neighbor_context(self):
        n0 = self.ctx.Neuron(name='NEURON0')
        n1 = self.ctx.Neuron(name='NEURON1')
        ctx1 = Context(ident='http://example.org/ctx1')
        n0.neighbor(n1)
        self.assertEqual(set(), set(ctx1(n0).neighbor()))

    def test_connection_get_staged(self):
        n0 = self.ctx.Neuron(name='NEURON0')
        n1 = self.ctx.Neuron(name='NEURON1')
        n0.connection(self.ctx.Connection(pre_cell=n0, post_cell=n1, syntype='send'))
        self.assertEqual(1, len(n0.connection()))

    def test_connection_only_defined(self):
        n0 = self.ctx.Neuron(name='NEURON0')
        n0.connection(self.ctx.Connection())
        self.assertEqual(0, len(n0.connection()))

    def test_connection_context(self):
        n0 = self.ctx.Neuron(name='NEURON0')
        n1 = self.ctx.Neuron(name='NEURON1')
        ctx1 = Context(ident='http://example.org/ctx1')
        n0.connection(self.ctx.Connection(pre_cell=n0, post_cell=n1, syntype='send'))
        self.assertEqual(set(), set(ctx1(n0).connection()))

    def test_init_from_lineage_name(self):
        c = self.ctx.Neuron(lineageName="AB plapaaaap", name="ADAL")
        self.save()
        for x in self.TestConfig['rdf.graph'].quads((None, None, None, None)):
            print(' '.join(y.n3() for y in x))
        c = self.context.stored(Neuron)(lineageName="AB plapaaaap")
        print(c.context)
        self.assertEqual(c.name(), 'ADAL')
