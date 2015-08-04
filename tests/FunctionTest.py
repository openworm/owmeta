import sys
sys.path.insert(0,".")
import unittest
import neuroml
import neuroml.writers as writers
import PyOpenWorm
from PyOpenWorm import *
import networkx
import rdflib
import rdflib as R
import pint as Q
import os
import subprocess as SP
import subprocess
import tempfile
import doctest

from glob import glob

from GraphDBInit import *

from DataTestTemplate import _DataTest

class FunctionTest(unittest.TestCase):
    """
    Setup and call functions individually,
    to allow profiling them in isolation.
    """

    def setUp(self):
        connect()

    def tearDown(self):
        disconnect()

    def test_list_synapses(self):
        """
        List synapses from the entire network.
        """
        w = Worm()
        net = w.get_neuron_network()
        syns = list(net.synapses())

        assert type(syns) == list

    def test_get_neurons(self):
        """
        List all the Neurons in the connectome.
        """
        ns = list(Neuron().load())

        assert len(ns) == 302

