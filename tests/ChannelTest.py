from __future__ import absolute_import
from owmeta import config
from owmeta.data import DataUser
from .DataTestTemplate import _DataTest

from owmeta.channel import Channel
from owmeta.cell import Cell


class ChannelTest(_DataTest):
    ctx_classes = (Cell, Channel)

    def test_DataUser(self):
        """
        Test that the Channel object is a DataUser object as well.
        """
        do = Channel('', conf=self.config)
        self.assertTrue(isinstance(do, DataUser))

    def test_same_name_same_id(self):
        """
        Test that two Channel objects with the same name have the same
        identifier. Saves us from having too many inserts of the same object.
        """
        c = Channel(name="boots")
        c1 = Channel(name="boots")
        self.assertEqual(c.identifier, c1.identifier)

    def test_channel_get_set(self):
        c1 = self.ctx.Channel(name="K+")
        c2 = self.ctx.Channel(name="Na+")
        cell = self.ctx.Cell(name='cell')
        cell.channel(c1)
        cell.channel(c2)
        self.save()

        cell = self.ctx.Cell(name='cell')
        self.assertEqual(set(cell.channel()), set([c1, c2]))

    def test_set_channel_get_appearsIn(self):
        c1 = self.ctx.Channel(name='K+')
        c2 = self.ctx.Channel(name='Na+')
        cell = self.ctx.Cell(name='cell')
        cell.channel(c1)
        cell.channel(c2)
        self.save()

        chan = self.ctx.Channel(name='K+')
        self.assertEqual(set([cell]), set(chan.appearsIn()))

    def test_set_appearsIn_get_channel(self):
        c1 = self.ctx.Channel(name='K+')
        c2 = self.ctx.Channel(name='Na+')

        cell = self.ctx.Cell(name='cell')
        c1.appearsIn(cell)
        c2.appearsIn(cell)

        self.save()

        cell = self.ctx.Cell(name='cell')
        self.assertEqual(set([c1, c2]), set(cell.channel()))

    def test_set_appearsIn_channel_property_in_graph(self):
        chan = self.ctx.Channel(name='K+')
        cell = self.ctx.Cell(name='cell')
        chan.appearsIn(cell)
        self.save()

        self.assertIn((cell.identifier,
                       cell.channel.link,
                       chan.identifier),
                      self.config['rdf.graph'])

    def test_property_in_graph(self):
        chan = self.ctx.Channel(name='K+')
        cell = self.ctx.Cell(name='cell')
        chan.appearsIn(cell)
        self.save()

        self.assertIn((chan.identifier,
                       chan.appearsIn.link,
                       cell.identifier),
                      self.config['rdf.graph'])
