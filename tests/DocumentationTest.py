# -*- coding: utf-8 -*-

from __future__ import absolute_import
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

class DocumentationTest(unittest.TestCase):
    def test_readme(self):
        [failure_count, return_count] = doctest.testfile("../README.md")
        self.assertEqual(failure_count, 0)
