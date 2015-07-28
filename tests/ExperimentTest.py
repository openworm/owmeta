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
    def test_DataUser(self):
        do = Experiment('', conf=self.config)
        self.assertTrue(isinstance(do, DataUser))

