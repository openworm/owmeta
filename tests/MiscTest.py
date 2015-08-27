# -*- coding: utf-8 -*-
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

class MiscTest(_DataTest):
    """Miscellaneous tests that have cropped up"""
    @unittest.expectedFailure
    def test_generators_do_not_reset(self):
        """
        This is for issue #175.  For some reason,
        the generators were being reset when called,
        meaning that the second call to len(list(neurons))
        below returned 0.
        """

        net = Worm().neuron_network()
        neurons = net.neuron_names()
        check1 = len(list(neurons))
        check2 = len(list(neurons))
        self.assertEqual(check1, check2)
