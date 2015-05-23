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

class PintTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.ur = Q.UnitRegistry()
        self.Q = self.ur.Quantity
    def test_atomic_short(self):
        q = self.Q(23, "mL")
        self.assertEqual("milliliter", str(q.units))
        self.assertEqual(23, q.magnitude)

    def test_atomic_long_singular(self):
        q = self.Q(23, "milliliter")
        self.assertEqual("milliliter", str(q.units))
        self.assertEqual(23, q.magnitude)

    def test_atomic_long_plural(self):
        q = self.Q(23, "milliliters")
        self.assertEqual("milliliter", str(q.units))
        self.assertEqual(23, q.magnitude)

    def test_atomic_long_plural_to_string(self):
        #XXX: Maybe there's a way to have the unit name pluralized...
        q = self.Q(23, "milliliters")
        self.assertEqual("23 milliliter", str(q))

    def test_string_init_long_plural_to_string(self):
        #XXX: Maybe there's a way to have the unit name pluralized...
        q = self.Q("23 milliliters")
        self.assertEqual("23 milliliter", str(q))

    def test_string_init_short(self):
        q = self.Q("23 mL")
        self.assertEqual("milliliter", str(q.units))
        self.assertEqual(23, q.magnitude)

    def test_string_init_short_no_space(self):
        q = self.Q("23mL")
        self.assertEqual("milliliter", str(q.units))
        self.assertEqual(23, q.magnitude)

    def test_string_init_long_singular(self):
        q = self.Q("23 milliliter")
        self.assertEqual("milliliter", str(q.units))
        self.assertEqual(23, q.magnitude)

    def test_string_init_long_plural(self):
        q = self.Q("23 milliliters")
        self.assertEqual("milliliter", str(q.units))
        self.assertEqual(23, q.magnitude)

    def test_init_magnitude_with_string(self):
        """ Pint doesn't care if you don't give it a number """
        q = self.Q("23", "milliliters")
        self.assertEqual("milliliter", str(q.units))
        self.assertEqual("23", q.magnitude)

        q = self.Q("worm", "milliliters")
        self.assertEqual("worm", q.magnitude)
