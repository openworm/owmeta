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

class SimplePropertyTest(_DataTest):
    def __init__(self,*args,**kwargs):
        _DataTest.__init__(self,*args,**kwargs)
        id_tests = []

    # XXX: auto generate some of these tests...
    def test_same_value_same_id_empty(self):
        """
        Test that two SimpleProperty objects with the same name have the same identifier()
        """
        do = DataObject(ident=R.URIRef("http://example.org"))
        do1 = DataObject(ident=R.URIRef("http://example.org"))
        c = DataObject.DatatypeProperty("boots", do)
        c1 = DataObject.DatatypeProperty("boots", do1)
        self.assertEqual(c.identifier(),c1.identifier())

    def test_same_value_same_id_not_empty(self):
        """
        Test that two SimpleProperty with the same name have the same identifier()
        """
        do = DataObject(ident=R.URIRef("http://example.org"))
        do1 = DataObject(ident=R.URIRef("http://example.org"))
        c = DataObject.DatatypeProperty("boots", do)
        c1 = DataObject.DatatypeProperty("boots", do1)
        do.boots('partition')
        do1.boots('partition')
        self.assertEqual(c.identifier(),c1.identifier())

    def test_same_value_same_id_not_empty_object_property(self):
        """
        Test that two SimpleProperty with the same name have the same identifier()
        """
        do = DataObject(ident=R.URIRef("http://example.org"))
        do1 = DataObject(ident=R.URIRef("http://example.org"))
        dz = DataObject(ident=R.URIRef("http://example.org/vip"))
        dz1 = DataObject(ident=R.URIRef("http://example.org/vip"))
        c = DataObject.ObjectProperty("boots", do)
        c1 = DataObject.ObjectProperty("boots", do1)
        do.boots(dz)
        do1.boots(dz1)
        self.assertEqual(c.identifier(),c1.identifier())

    def test_diff_value_diff_id_not_empty(self):
        """
        Test that two SimpleProperty with the same name have the same identifier()
        """
        do = DataObject(ident=R.URIRef("http://example.org"))
        do1 = DataObject(ident=R.URIRef("http://example.org"))
        c = DataObject.DatatypeProperty("boots", do)
        c1 = DataObject.DatatypeProperty("boots", do1)
        do.boots('join')
        do1.boots('partition')
        self.assertNotEqual(c.identifier(),c1.identifier())

    def test_diff_prop_same_name_same_object_same_value_same_id(self):
        """
        Test that two SimpleProperty with the same name have the same identifier()
        """
        # why would you ever do this?
        do = DataObject(ident=R.URIRef("http://example.org"))
        c = DataObject.DatatypeProperty("boots", do)
        c1 = DataObject.DatatypeProperty("boots", do)
        c('join')
        c1('join')
        self.assertEqual(c.identifier(),c1.identifier())

    def test_diff_prop_same_name_same_object_diff_value_same_id(self):
        """
        Test that two SimpleProperty with the same name have the same identifier()
        """
        # why would you ever do this?
        do = DataObject(ident=R.URIRef("http://example.org"))
        c = DataObject.DatatypeProperty("boots", do)
        c1 = DataObject.DatatypeProperty("boots", do)
        c('partition')
        c1('join')
        self.assertNotEqual(c.identifier(),c1.identifier())

    def test_diff_value_insert_order_same_id(self):
        """
        Test that two SimpleProperty with the same name have the same identifier()
        """
        do = DataObject(ident=R.URIRef("http://example.org"))
        do1 = DataObject(ident=R.URIRef("http://example.org"))
        c = DataObject.DatatypeProperty("boots", do)
        c1 = DataObject.DatatypeProperty("boots", do1)
        do.boots('join')
        do.boots('simile')
        do.boots('partition')
        do1.boots('partition')
        do1.boots('join')
        do1.boots('simile')
        self.assertEqual(c.identifier(),c1.identifier())

    def test_diff_value_insert_order_same_id_object_property(self):
        """
        Test that two SimpleProperty with the same name have the same identifier()
        """
        do = DataObject(ident=R.URIRef("http://example.org"))
        do1 = DataObject(ident=R.URIRef("http://example.org"))
        oa = DataObject(ident=R.URIRef("http://example.org/a"))
        ob = DataObject(ident=R.URIRef("http://example.org/b"))
        oc = DataObject(ident=R.URIRef("http://example.org/c"))

        c = DataObject.ObjectProperty("boots", do)
        c1 = DataObject.ObjectProperty("boots", do1)

        do.boots(oa)
        do.boots(ob)
        do.boots(oc)
        do1.boots(oc)
        do1.boots(oa)
        do1.boots(ob)
        self.assertEqual(c.identifier(),c1.identifier())

    def test_triples_with_no_value(self):
        """ Test that when there is no value set for a property, it still yields triples """
        do = DataObject(ident=R.URIRef("http://example.org"))
        class T(SimpleProperty):
            property_type = 'DatatypeProperty'
            linkName = 'test'
            owner_type = DataObject

        sp = T(owner=do)
        self.assertEqual(len(list(sp.triples())), 0)
        self.assertEqual(len(list(sp.triples(query=True))), 0)
