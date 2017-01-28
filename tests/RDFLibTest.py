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

class RDFLibTest(unittest.TestCase):
    """Tests RDFLib, our backend library that interfaces with the database as an
       RDF graph."""

    @classmethod
    def setUpClass(cls):
        cls.ns = {"ns1" : "http://example.org/"}
    def test_uriref_not_url(self):
        try:
            rdflib.URIRef("daniel@example.com")
        except:
            self.fail("Doesn't actually fail...which is weird")
    def test_uriref_not_id(self):
        """ Test that rdflib throws up a warning when we do something bad """
        #XXX: capture the logged warning
        import cStringIO
        import logging

        out = cStringIO.StringIO()
        logger = logging.getLogger()
        stream_handler = logging.StreamHandler(out)
        logger.addHandler(stream_handler)
        try:
            rdflib.URIRef("some random string")
        finally:
            logger.removeHandler(stream_handler)
        v = out.getvalue()
        out.close()
        self.assertRegexpMatches(str(v), r".*some random string.*")

    def test_BNode_equality1(self):
        a = rdflib.BNode("some random string")
        b = rdflib.BNode("some random string")
        self.assertEqual(a, b)

    def test_BNode_equality2(self):
        a = rdflib.BNode()
        b = rdflib.BNode()
        self.assertNotEqual(a, b)
