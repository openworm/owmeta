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

class ExperimentTest(_DataTest):

    def test_data_user(self):
        """
        Test that the Experiment object is a DataUser object as well.
        """ 
        do = Experiment('', conf=self.config)
        self.assertTrue(isinstance(do, DataUser))

    def test_unimplemented_conditions(self):
        """
        Test that an Experiment with no conditions attribute raises an
        error when get_conditions() is called.
        """
        ex = Experiment()
        with self.assertRaises(NotImplementedError):
            ex.get_conditions()

