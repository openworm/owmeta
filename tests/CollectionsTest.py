from __future__ import absolute_import
from PyOpenWorm.collections import Bag
from .DataTestTemplate import _DataTest
import rdflib


class BagTest(_DataTest):

    def test_bag_init(self):
        b = Bag(name="bah", value=12)
        b.value(55)
        b.add(545)
        b.value(Bag(name="humbug"))
        self.assertEqual(Bag.rdf_namespace['bah'], b.identifier)
