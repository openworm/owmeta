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

class DataObjectTest(_DataTest):

    def test_DataUser(self):
        do = DataObject()
        self.assertTrue(isinstance(do,PyOpenWorm.DataUser))

    def test_identifier(self):
        """ Test that we can set and return an identifier """
        do = DataObject(ident="http://example.org")
        self.assertEqual(do.identifier(), R.URIRef("http://example.org"))

    @unittest.skip("Should be tracked by version control")
    def test_uploader(self):
        """ Make sure that we're marking a statement with it's uploader """
        g = make_graph(20)
        r = DataObject(triples=g,conf=self.config)
        r.save()
        u = r.uploader()
        self.assertEqual(self.config['user.email'], u)

    def test_object_from_id(self):
        do = DataObject(ident="http://example.org")
        g = do.object_from_id('http://openworm.org/entities/Neuron')
        self.assertIsInstance(g,Neuron)
        g = do.object_from_id('http://openworm.org/entities/Connection')
        self.assertIsInstance(g,Connection)

    @unittest.skip("Should be tracked by version control")
    def test_upload_date(self):
        """ Make sure that we're marking a statement with it's upload date """
        g = make_graph(20)
        r = DataObject(triples=g)
        r.save()
        u = r.upload_date()
        self.assertIsNotNone(u)
