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

class WormTest(_DataTest):
    """Test for Worm."""
    def setUp(self):
        _DataTest.setUp(self)
        ns = self.config['rdf.namespace']
        self.trips = [(ns['64'], ns['356'], ns['184']),
                (ns['john'], R.RDF['type'], ns['Connection']),
                (ns['john'], ns['Connection/pre'], ns['64']),
                (ns['64'], R.RDFS['label'], R.Literal("PVCR")),
                (ns['john'], ns['Connection/syntype'], ns['356']),
                (ns['john'], ns['Connection/number'], R.Literal('1', datatype=R.XSD.integer)),
                (ns['184'], R.RDFS['label'], R.Literal("AVAL")),
                (ns['john'], ns['Connection/post'], ns['184']),
                (ns['65'], ns['356'], ns['185']),
                (ns['luke'], R.RDF['type'], ns['Connection']),
                (ns['luke'], ns['Connection/pre'], ns['65']),
                (ns['65'], R.RDFS['label'], R.Literal("PVCL")),
                (ns['luke'], ns['Connection/syntype'], ns['356']),
                (ns['luke'], ns['Connection/number'], R.Literal('1', datatype=R.XSD.integer)),
                (ns['185'], R.RDFS['label'], R.Literal("AVAR")),
                (ns['luke'], ns['Connection/post'], ns['185'])]

    def test_get_network(self):
        w = Worm()
        w.neuron_network(Network())
        w.save()
        self.assertIsInstance(Worm().get_neuron_network(), Network)

    def test_muscles1(self):
        w = Worm()
        w.muscle(Muscle(name='MDL08'))
        w.muscle(Muscle(name='MDL15'))
        w.save()
        self.assertIn(Muscle(name='MDL08'), list(Worm().muscles()))
        self.assertIn(Muscle(name='MDL15'), list(Worm().muscles()))

    def test_get_semantic_net(self):
        g0 = Worm().get_semantic_net()
        self.assertTrue(isinstance(g0, rdflib.ConjunctiveGraph))
