"""
Not actually tests, but benchmarks.
"""
from __future__ import print_function
from PyOpenWorm import Neuron, Connection, connect, disconnect
from PyOpenWorm.data import ZODBSource
import gc
import tempfile
import random
import transaction
import os
import shutil
from rdflib.term import URIRef

NUM_TRIPLES = 10000
baseline_graph = None
baseline_source = None
baseline_graph_directory = None


def initialize_baseline_graph():
    global baseline_graph, baseline_source, baseline_graph_directory
    baseline_source = ZODBSource()
    baseline_graph_directory = tempfile.mkdtemp()
    baseline_source.conf = {
            'rdf.store_conf': os.path.join(baseline_graph_directory, 'db')
            }
    baseline_source.open()
    baseline_graph = baseline_source.graph
    for s in range(NUM_TRIPLES):
        baseline_graph.add((URIRef('http://example.com/s' + str(s)),
                            URIRef('http://example.com/p' + str(s / 1000)),
                            URIRef('http://example.com/o' + str(s))))
    transaction.commit()


def destroy_baseline_graph():
    baseline_source.close()
    shutil.rmtree(baseline_graph_directory)


def setup():
    connect(configFile='tests/data_integrity_test.conf')
    reinitialize()


def reinitialize():
    baseline_initialize()
    gc.collect()


def teardown():
    disconnect()


def baseline_initialize():
    baseline()
    baseline()


def baseline():
    sequence = list(range(0, NUM_TRIPLES, 1000))
    random.shuffle(sequence)
    sequence = sorted(sequence[0:NUM_TRIPLES]) + sequence[NUM_TRIPLES:-1]

    for x in sequence:
        list(baseline_graph.triples((None, 'http://example.com/p' + str(x), None)))


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
