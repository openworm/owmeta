# -*- coding: utf-8 -*-

from __future__ import absolute_import
import unittest
import rdflib

class RDFLibTest(unittest.TestCase):
    """Tests RDFLib, our backend library that interfaces with the database as an
       RDF graph."""

    @classmethod
    def setUpClass(cls):
        cls.ns = {"ns1" : "http://example.org/"}
    def test_uriref_not_url(self):
        try:
            rdflib.URIRef("daniel@example.com")
        except Exception:
            self.fail("Doesn't actually fail...which is weird")
    def test_uriref_not_id(self):
        """ Test that rdflib throws up a warning when we do something bad """
        import six
        import logging

        out = six.StringIO()
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
