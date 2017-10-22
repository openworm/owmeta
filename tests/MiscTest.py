# -*- coding: utf-8 -*-
from __future__ import absolute_import
from yarom import yarom_import
from PyOpenWorm import connect, disconnect, config
from .DataTestTemplate import _DataTest

Worm = yarom_import('PyOpenWorm.worm.Worm')


class MiscTest(_DataTest):
    """Miscellaneous tests that have cropped up"""

    def setUp(self):
        connect(configFile='tests/data_integrity_test.conf')
        self.g = config("rdf.graph")

    def tearDown(self):
        disconnect()

    def test_generators_do_not_reset(self):
        """
        This is for issue #175.  For some reason,
        the generators were being reset when called,
        meaning that the second call to len(list(neurons))
        below returned 0.
        """

        net = Worm().neuron_network()
        neurons = net.neurons()
        check1 = len(list(neurons))
        check2 = len(list(neurons))
        self.assertEqual(check1, check2)
