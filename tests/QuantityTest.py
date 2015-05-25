# -*- coding: utf-8 -*-

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

class QuantityTest(unittest.TestCase):
    def test_string_init_short(self):
        q = Quantity.parse("23 mL")
        self.assertEqual("milliliter", q.unit)
        self.assertEqual(23, q.value)

    def test_string_init_volume(self):
        q = Quantity.parse("23 inches^3")
        self.assertEqual("inch ** 3", q.unit)
        self.assertEqual(23, q.value)

    def test_string_init_compound(self):
        q = Quantity.parse("23 inches/second")
        self.assertEqual("inch / second", q.unit)
        self.assertEqual(23, q.value)

    def test_atomic_short(self):
        q = Quantity(23, "mL")
        self.assertEqual("milliliter", q.unit)
        self.assertEqual(23, q.value)

    def test_atomic_long(self):
        q = Quantity(23, "milliliters")
        self.assertEqual("milliliter", q.unit)
        self.assertEqual(23, q.value)
