from __future__ import print_function
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

class NeuronTest(_DataTest):
    @classmethod
    def setUpClass(cls):
        import logging
        #logging.basicConfig(level=logging.DEBUG)

    def setUp(self):
        _DataTest.setUp(self)
        self.neur = lambda x : Neuron(name=x)

    def test_Cell(self):
        do = self.neur('BDUL')
        self.assertTrue(isinstance(do,Cell))

    def test_receptors(self):
        n = self.neur('AVAL')
        n.receptor('GLR-2')
        n.save()
        self.assertIn('GLR-2', list(self.neur('AVAL').receptors()))

    def test_same_name_same_id(self):
        """
        Test that two Neuron objects with the same name have the same identifier()
        Saves us from having too many inserts of the same object.
        """
        c = Neuron(name="boots")
        c1 = Neuron(name="boots")
        self.assertEqual(c.identifier(),c1.identifier())

    def test_type(self):
        n = self.neur('AVAL')
        n.type('interneuron')
        n.save()
        self.assertEqual('interneuron', self.neur('AVAL').type.one())

    def test_name(self):
        """ Test that the name property is set when the neuron is initialized with it """
        self.assertEqual('AVAL', self.neur('AVAL').name())
        self.assertEqual('AVAR', self.neur('AVAR').name())

    def test_neighbor(self):
        n = self.neur('AVAL')
        n.neighbor(self.neur('PVCL'), syntype='send')
        neighbors = list(n.neighbor())
        self.assertIn(self.neur('PVCL'), neighbors)
        g = R.Graph()
        for t in n.triples():
            g.add(t)
        n.save()
        self.assertIn(self.neur('PVCL'), list(self.neur('AVAL').neighbor()))

    def test_init_from_lineage_name(self):
        c = Neuron(lineageName="AB plapaaaap",name="ADAL")
        c.save()
        c = Neuron(lineageName="AB plapaaaap")
        self.assertEqual(c.name(), 'ADAL')
