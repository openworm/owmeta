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

class ChannelTest(_DataTest):

    def test_DataUser(self):
        """
        Test that the Channel object is a DataUser object as well.
        """
        do = Channel('', conf=self.config)
        self.assertTrue(isinstance(do, DataUser))

    def test_same_name_same_id(self):
        """
        Test that two Channel objects with the same name have the same identifier()
        Saves us from having too many inserts of the same object.
        """
        c = Channel(name="boots")
        c1 = Channel(name="boots")
        self.assertEqual(c.identifier(),c1.identifier())

