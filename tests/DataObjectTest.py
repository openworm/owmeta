import sys
sys.path.insert(0, ".")
import unittest
import PyOpenWorm
from PyOpenWorm import DataObject, Neuron, Connection
import rdflib as R
from GraphDBInit import make_graph

from DataTestTemplate import _DataTest


class DataObjectTest(_DataTest):

    def test_DataUser(self):
        do = DataObject()
        self.assertTrue(isinstance(do, PyOpenWorm.DataUser))

    def test_identifier(self):
        """ Test that we can set and return an identifier """
        do = DataObject(ident="http://example.org")
        self.assertEqual(do.identifier(), R.URIRef("http://example.org"))

    @unittest.skip("Should be tracked by version control")
    def test_uploader(self):
        """ Make sure that we're marking a statement with it's uploader """
        g = make_graph(20)
        r = DataObject(triples=g, conf=self.config)
        r.save()
        u = r.uploader()
        self.assertEqual(self.config['user.email'], u)

    def test_object_from_id(self):
        do = DataObject(ident="http://example.org")
        g = do.object_from_id('http://openworm.org/entities/Neuron')
        self.assertIsInstance(g, Neuron)
        g = do.object_from_id('http://openworm.org/entities/Connection')
        self.assertIsInstance(g, Connection)

    @unittest.skip("Should be tracked by version control")
    def test_upload_date(self):
        """ Make sure that we're marking a statement with it's upload date """
        g = make_graph(20)
        r = DataObject(triples=g)
        r.save()
        u = r.upload_date()
        self.assertIsNotNone(u)

    def test_triples_cycle(self):
        """ Test that no duplicate triples are released when there's a cycle in the graph """
        class T(DataObject):
            objectProperties = ['s']

        t = DataObject(ident=R.URIRef("http://example.org"))
        s = DataObject(ident=R.URIRef("http://example.org"))
        DataObject.ObjectProperty("s", t)
        DataObject.ObjectProperty("s", s)
        t.s(s)
        s.s(t)

        seen = set()
        for x in t.triples(query=True):
            if (x in seen):
                self.fail("got a duplicate: " + str(x))
            else:
                seen.add(x)

    def test_triples_clone_sibling(self):
        """ Test that no duplicate triples are released when there's a clone in the graph.

        For example: A->B
                     |
                     +->C->B
        This is to avoid the simple 'guard' solution in triples which would output B
        twice.
        """
        class T(Y.DataObject):
            objectProperties = ['s']

        t = T(key="a")
        s = T(key="b")
        v = T(key="c")
        t.s(s)
        t.s(v)
        v.s(s)
        seen = set()
        for x in t.triples(query=True):
            if (x in seen):
                self.fail("got a duplicate: " + str(x))
            else:
                seen.add(x)

    def test_property_matching_method_name(self):
        """ Creating a property with the same name as a method should be disallowed """
        class T(DataObject):
            objectProperties = ['load']
        with self.assertRaises(Exception):
            T()
