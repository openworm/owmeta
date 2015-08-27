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

class PlotTest(_DataTest):

    def test_DataUser(self):
        """
        Test that the Plot object is a DataUser object as well.
        """
        do = Plot('', conf=self.config)
        self.assertTrue(isinstance(do, DataUser))

    def test_no_data_error(self):
        """
        Is the correct error raised when we try to
        do get_data with no data?
        """
        pl = Plot()
        with self.assertRaises(AttributeError):
            pl.get_data()

    def test_incorrect_input_error(self):
        """
        Is the correct error raised when we try to instantiate
        with non-2D-list data?
        """
        with self.assertRaises(ValueError):
            pl = Plot(data=['a', 'b'])

    def test_successful_get_data(self):
        """
        Can we retrieve the data we input?
        """
        ary = [[1,2],[3,4]]
        pl = Plot(data=ary)
        assert pl.get_data() == ary

