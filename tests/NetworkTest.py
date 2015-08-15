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

class NetworkTest(_DataTest):
    def setUp(s):
        _DataTest.setUp(s)
        s.net = Network(conf=s.config)

    def test_aneuron(self):
        """
        Test that we can retrieve a Neuron by name.
        """
        self.assertTrue(isinstance(self.net.aneuron('AVAL'),PyOpenWorm.Neuron))

    def test_neurons(self):
        """
        Test that we can access arbitrary Neurons,
        and that they are in the Network
        """
        neuron_1 = self.net.aneuron('AVAL')
        neuron_2 = self.net.aneuron('DD5')
        self.assertTrue(neuron_1 in net.neurons())
        self.assertTrue(neuron_2 in net.neurons())

    def test_synapses_rdf(self):
        """ Check that synapses() returns connection objects """
        for x in self.net.synapse():
            self.assertIsInstance(x,Connection)
            break

    def test_as_networkx(self):
        """Test that as_networkx returns the correct type."""
        self.assertTrue(isinstance(self.net.as_networkx(),networkx.DiGraph))
