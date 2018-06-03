from __future__ import absolute_import
from __future__ import print_function
import unittest
from PyOpenWorm.data import DataUser
from PyOpenWorm.dataObject import DataObject, DatatypeProperty
from PyOpenWorm.neuron import Neuron
from PyOpenWorm.connection import Connection
import rdflib as R
from .GraphDBInit import make_graph

from .DataTestTemplate import _DataTest


class DataObjectTest(_DataTest):

    def test_DataUser(self):
        do = DataObject()
        self.assertTrue(isinstance(do, DataUser))

    def test_identifier(self):
        """ Test that we can set and return an identifier """
        do = DataObject(ident="http://example.org")
        self.assertEqual(do.identifier, R.URIRef("http://example.org"))

    @unittest.skip("Should be tracked by version control")
    def test_uploader(self):
        """ Make sure that we're marking a statement with it's uploader """
        g = make_graph(20)
        r = DataObject(triples=g, conf=self.config)
        r.save()
        u = r.uploader()
        self.assertEqual(self.config['user.email'], u)

    def test_object_from_id_type_0(self):
        g = DataObject.object_from_id('http://openworm.org/entities/Neuron')
        self.assertIsInstance(g, Neuron)

    def test_object_from_id_type_1(self):
        g = DataObject.object_from_id('http://openworm.org/entities/Connection')
        self.assertIsInstance(g, Connection)

    @unittest.skip("Should be tracked by version control")
    def test_upload_date(self):
        """ Make sure that we're marking a statement with it's upload date """
        g = make_graph(20)
        r = DataObject(triples=g)
        r.save()
        u = r.upload_date()
        self.assertIsNotNone(u)

    def test_repr(self):
        self.assertRegexpMatches(repr(DataObject(ident="http://example.com")),
                                 r"DataObject\(ident=rdflib\.term\.URIRef\("
                                 r"u?[\"']http://example.com[\"']\)\)")

    def test_properties_are_init_args(self):
        class A(DataObject):
            a = DatatypeProperty()
            properties_are_init_args = True
        a = A(a=5)
        self.assertEqual(5, a.a())

    def test_properties_are_init_args_subclass_override(self):
        class A(DataObject):
            a = DatatypeProperty()
            properties_are_init_args = True

        class B(A):
            b = DatatypeProperty()
            properties_are_init_args = False

        with self.assertRaises(TypeError):
            B(a=5)

    def test_properties_are_init_args_subclass_parent_unchanged(self):
        class A(DataObject):
            a = DatatypeProperty()
            properties_are_init_args = True

        class B(A):
            b = DatatypeProperty()
            properties_are_init_args = False

        a = A(a=5)
        self.assertEqual(5, a.a())

    def test_properties_are_init_args_subclass_explicit(self):
        class A(DataObject):
            a = DatatypeProperty()
            properties_are_init_args = True

        class B(A):
            def __init__(self, a=None, **kw):
                super(B, self).__init__(**kw)
                pass

        b = B(a=5)
        self.assertIsNone(b.a())

    def test_rdfs_comment_property(self):
        a = DataObject(rdfs_comment='Hello')
        self.assertIn('Hello', a.rdfs_comment())
