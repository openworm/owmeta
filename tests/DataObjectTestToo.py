import sys
sys.path.insert(0,".")
import unittest
import neuroml
import neuroml.writers as writers
import PyOpenWorm
from PyOpenWorm import *
import test_data as TD
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


class DataObjectTestToo(unittest.TestCase):
    def test_helpful_message_on_non_connection(self):
        """ The message should say something about connecting """
        Configureable.conf = False # Ensure that we are disconnected
        with self.assertRaisesRegexp(Exception, ".*[cC]onnect.*"):
            do = DataObject()
