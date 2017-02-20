"""
Not actually tests, but benchmarks.
"""
from __future__ import print_function
from .DataTestTemplate import _DataTest
from PyOpenWorm import Neuron, Connection, connect, disconnect, config


class ProfileTest(_DataTest):
    def setUp(self):
        connect(configFile='tests/data_integrity_test.conf')
        self.g = config("rdf.graph")

    def tearDown(self):
        disconnect()

    def test_adal_connections(self):
        """
        See github issue openworm/PyOpenWorm#90
        """
        adal = Neuron("ADAL")
        post = Neuron()
        Connection(pre_cell=adal, post_cell=post)
        tuple(post.load())

    def test_neuron_receptors(self):
        post = Neuron()
        list(post.receptor())
