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
from nose import with_setup

class Quantity_Test():
    def test_string_init_short(self):
        q = Quantity.parse("23 mL")
        assert "milliliter" == q.unit
        assert 23 == q.value

    def test_string_init_volume(self):
        q = Quantity.parse("23 inches^3")
        assert "inch ** 3" == q.unit
        assert 23 == q.value

    def test_string_init_compound(self):
        q = Quantity.parse("23 inches/second")
        assert "inch / second" == q.unit
        assert 23 == q.value

    def test_atomic_short(self):
        q = Quantity(23, "mL")
        assert "milliliter" == q.unit
        assert 23 == q.value

    def test_atomic_long(self):
        q = Quantity(23, "milliliters")
        assert "milliliter" == q.unit
        assert 23 == q.value
