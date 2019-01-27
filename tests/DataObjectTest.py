from __future__ import absolute_import
from __future__ import print_function
import unittest
import rdflib as R
import six
import warnings

from yarom.utils import FCN

from PyOpenWorm.data import DataUser
from PyOpenWorm.dataObject import DataObject, DatatypeProperty, _partial_property
from PyOpenWorm.neuron import Neuron
from PyOpenWorm.connection import Connection
from PyOpenWorm.context import Context
from PyOpenWorm import BASE_CONTEXT

from .GraphDBInit import make_graph

from .DataTestTemplate import _DataTest
try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch


DATAOBJECT_PROPERTIES = ['DatatypeProperty', 'ObjectProperty', 'UnionProperty']


class DataObjectTest(_DataTest):
    ctx_classes = (DataObject,)

    def setUp(self):
        super(DataObjectTest, self).setUp()
        self.patcher = patch('PyOpenWorm.data', 'ALLOW_UNCONNECTED_DATA_USERS', True)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        super(DataObjectTest, self).tearDown()

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
        g = self.ctx.DataObject.object_from_id('http://openworm.org/entities/Neuron')
        self.assertIsInstance(g, Neuron)

    def test_object_from_id_type_1(self):
        g = self.ctx.DataObject.object_from_id('http://openworm.org/entities/Connection')
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

        if six.PY2:
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                B(a=5)
                self.assertTrue(len(w) > 0 and issubclass(w[0].category, DeprecationWarning))
        else:
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

    def test_load_unloaded_subtype(self):
        '''
        This test actually combines a few different features:
            - loading a module from a ClassDescription
            - resolving subclasses from superclasses
        '''
        from PyOpenWorm.dataObject import PythonModule, PythonClassDescription, RegistryEntry

        ident = R.URIRef('http://openworm.org/entities/TDO01')
        rdftype = R.RDF['type']
        sc = R.RDFS['subClassOf']
        tdo = R.URIRef('http://openworm.org/entities/TDO')
        pm = R.URIRef('http://example.com/pymod')
        pcd = R.URIRef('http://example.com/pycd')
        re = R.URIRef('http://example.com/re')
        g = R.ConjunctiveGraph()
        ctx = g.get_context(self.context.identifier)
        self.TestConfig['rdf.graph'] = g
        trips = [(ident, rdftype, tdo),
                 (tdo, sc, DataObject.rdf_type),
                 (pm, rdftype, PythonModule.rdf_type),
                 (pm, PythonModule.name.link, R.Literal('tests.tmod.tdo')),
                 (pcd, PythonClassDescription.name.link, R.Literal('TDO')),
                 (pcd, rdftype, PythonClassDescription.rdf_type),
                 (pcd, PythonClassDescription.module.link, pm),
                 (re, rdftype, RegistryEntry.rdf_type),
                 (re, RegistryEntry.rdf_class.link, tdo),
                 (re, RegistryEntry.class_description.link, pcd)]
        for tr in trips:
            ctx.add(tr)
        o = list(self.context.stored(DataObject)(ident=ident).load())
        self.assertEqual('tests.tmod.tdo.TDO', FCN(type(o[0])))

    def test_save_load_subtype(self):

        class A(DataObject):
            class_context = self.context
        self.context.mapper.process_class(A)

        self.context.add_import(BASE_CONTEXT)
        m = self.context(Context)(ident='http://example.org/ctx', imported=(self.context,))
        im = self.context(Context)(ident='http://example.org/ctxim', imported=(self.context,))
        co = self.context(Context)(ident='http://example.org/ctxb', imported=(m, im))
        m(A)(ident='http://example.org/anA')
        co.save_imports(im)
        co.save_context(inline_imports=True)

        o = list(m.stored(DataObject)(ident='http://example.org/anA').load())
        self.assertIsInstance(o[0], A)

    def test_context_getter(self):
        a = DataObject()
        self.assertIsNone(a.context)

    def test_context_setter(self):
        a = DataObject()
        a.context = 42
        self.assertEquals(a.context, 42)

    def test_dataobject_property_that_generate_partial_property(self):
        for property_classmethod in DATAOBJECT_PROPERTIES:
            partial_property = getattr(DataObject, property_classmethod)()
            self.assertIsInstance(partial_property, _partial_property)

    def test_dataobject_property_that_return_owner(self):
        for property_classmethod in DATAOBJECT_PROPERTIES:
            owner = Mock()
            getattr(DataObject, property_classmethod)(owner=owner, linkName="")
            owner.attach_property.assert_called_once()
