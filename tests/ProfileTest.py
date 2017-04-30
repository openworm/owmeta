"""
Not actually tests, but benchmarks.
"""
from __future__ import print_function
from PyOpenWorm import Neuron, Connection, connect, disconnect, config


def setup():
    connect(configFile='tests/data_integrity_test.conf')


def teardown():
    disconnect()


def baseline():
    list(zip(range(1000), config('rdf.graph').triples((None, None, None))))


def test_adal_connections():
    """
    See github issue openworm/PyOpenWorm#90
    """
    for x in range(10):
        adal = Neuron("ADAL")
        post = Neuron()
        Connection(pre_cell=adal, post_cell=post)
        tuple(post.load())


def test_adal_connections_property():
    """
    See github issue openworm/PyOpenWorm#90
    """
    for x in range(10):
        adal = Neuron("ADAL")
        tuple(adal.connection.get('either'))


def test_neuron_receptors():
    for x in range(30):
        post = Neuron()
        list(post.receptor())


def test_neuron_load():
    list(Neuron().load())
