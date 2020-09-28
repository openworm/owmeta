"""
Not actually tests, but benchmarks.
"""
from __future__ import print_function
from owmeta.neuron import Neuron
from owmeta.connection import Connection
from owmeta_core import connect, disconnect

from .TestUtilities import xfail_without_db


connection = None


def setup():
    global connection
    xfail_without_db()
    connection = connect(configFile='tests/data_integrity_test.conf')


def teardown():
    disconnect(connection)


def test_adal_connections():
    """
    See github issue openworm/owmeta#90
    """
    for x in range(10):
        adal = Neuron("ADAL")
        post = Neuron()
        Connection(pre_cell=adal, post_cell=post)
        tuple(post.load())


def test_adal_connections_property():
    """
    See github issue openworm/owmeta#90
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
