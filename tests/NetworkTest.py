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
        Test that we can add arbitrary Neurons to the Network,
        and that they can be accessed afterwards.
        """
        self.net.neuron(Neuron(name='AVAL'))
        self.net.neuron(Neuron(name='DD5'))
        self.assertTrue('AVAL' in self.net.neuron_names())
        self.assertTrue('DD5' in self.net.neuron_names())

    def test_synapses_rdf(self):
        """ Check that synapses() returns connection objects """
        for x in self.net.synapse():
            self.assertIsInstance(x,Connection)
            break

    def test_as_networkx(self):
        """Test that as_networkx returns the correct type."""
        self.assertTrue(isinstance(self.net.as_networkx(),networkx.DiGraph))
