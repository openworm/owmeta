from __future__ import print_function
from __future__ import absolute_import
from yarom import yarom_import
import rdflib as R

from .DataTestTemplate import _DataTest

DataObject = yarom_import('PyOpenWorm.dataObject.DataObject')


class SimplePropertyTest(_DataTest):
    ctx_classes = (DataObject,)

    # XXX: auto generate some of these tests...
    def test_same_value_same_id_empty(self):
        do = self.ctx.DataObject(ident=R.URIRef("http://example.org"))
        do1 = self.ctx.DataObject(ident=R.URIRef("http://example.org"))
        c = DataObject.DatatypeProperty("boots", do)
        c1 = DataObject.DatatypeProperty("boots", do1)
        self.assertEqual(c.identifier, c1.identifier)

    def test_same_value_same_id_not_empty(self):
        do = self.ctx.DataObject(ident=R.URIRef("http://example.org"))
        do1 = self.ctx.DataObject(ident=R.URIRef("http://example.org"))
        c = DataObject.DatatypeProperty("boots", do)
        c1 = DataObject.DatatypeProperty("boots", do1)
        do.boots('partition')
        do1.boots('partition')
        self.assertEqual(c.identifier, c1.identifier)

    def test_same_value_same_id_not_empty_object_property(self):
        do = self.ctx.DataObject(ident=R.URIRef("http://example.org"))
        do1 = self.ctx.DataObject(ident=R.URIRef("http://example.org"))
        dz = self.ctx.DataObject(ident=R.URIRef("http://example.org/vip"))
        dz1 = self.ctx.DataObject(ident=R.URIRef("http://example.org/vip"))
        c = DataObject.ObjectProperty("boots", do)
        c1 = DataObject.ObjectProperty("boots", do1)
        do.boots(dz)
        do1.boots(dz1)
        self.assertEqual(c.identifier, c1.identifier)

    def test_diff_value_diff_id_equal(self):
        do = self.ctx.DataObject(ident=R.URIRef("http://example.org"))
        do1 = self.ctx.DataObject(ident=R.URIRef("http://example.org"))
        c = DataObject.DatatypeProperty("boots", do)
        c1 = DataObject.DatatypeProperty("boots", do1)
        do.boots('join')
        do1.boots('partition')
        self.assertEqual(c.identifier, c1.identifier)

    def test_diff_prop_same_name_same_object_same_value_same_id(self):
        do = self.ctx.DataObject(ident=R.URIRef("http://example.org"))
        c = DataObject.DatatypeProperty("boots", do)
        c1 = DataObject.DatatypeProperty("boots", do)
        c('join')
        c1('join')
        self.assertEqual(c.identifier, c1.identifier)

    def test_diff_prop_same_name_same_object_diff_value_same_id(self):
        do = self.ctx.DataObject(ident=R.URIRef("http://example.org"))
        c = DataObject.DatatypeProperty("boots", do)
        c1 = DataObject.DatatypeProperty("boots", do)
        c('partition')
        c1('join')
        self.assertEqual(c.identifier, c1.identifier)

    def test_diff_value_insert_order_same_id(self):
        do = self.ctx.DataObject(ident=R.URIRef("http://example.org"))
        do1 = self.ctx.DataObject(ident=R.URIRef("http://example.org"))

        print (list(self.context.contents_triples()))
        c = DataObject.DatatypeProperty("boots", do, multiple=True)
        c1 = DataObject.DatatypeProperty("boots", do1, multiple=True)
        do.boots('join')
        do.boots('simile')
        do.boots('partition')
        do1.boots('partition')
        do1.boots('join')
        do1.boots('simile')
        self.assertEqual(c.identifier, c1.identifier)

    def test_object_property_diff_value_insert_order_same_id(self):
        do = self.ctx.DataObject(ident=R.URIRef("http://example.org"))
        do1 = self.ctx.DataObject(ident=R.URIRef("http://example.org"))

        oa = self.ctx.DataObject(ident=R.URIRef("http://example.org/a"))
        ob = self.ctx.DataObject(ident=R.URIRef("http://example.org/b"))
        oc = self.ctx.DataObject(ident=R.URIRef("http://example.org/c"))

        c = DataObject.ObjectProperty("boots", do, multiple=True)
        c1 = DataObject.ObjectProperty("boots", do1, multiple=True)

        do.boots(oa)
        do.boots(ob)
        do.boots(oc)

        do1.boots(oc)
        do1.boots(oa)
        do1.boots(ob)

        self.assertEqual(c.identifier, c1.identifier)

    def test_property_get_returns_collection(self):
        """
        This is for issue #175.
        """

        do = self.ctx.DataObject(ident=R.URIRef("http://example.org"))
        do.boots = DataObject.DatatypeProperty(multiple=True)
        do.boots(4)
        # self.save()

        do = self.ctx.DataObject(ident=R.URIRef("http://example.org"))
        do.boots = DataObject.DatatypeProperty(multiple=True)

        x = do.boots()
        l1 = list(x)
        print(l1)
        b = list(x)
        self.assertEqual([4], b)


class POCacheTest(_DataTest):

    ctx_classes = (DataObject,)

    def setUp(self):
        super(POCacheTest, self).setUp()
        o = self.ctx.DataObject(ident=R.URIRef("http://example.org/a"))
        DataObject.DatatypeProperty("boots", o)
        o.boots('h')
        self.save()

    def test_cache_refresh_after_triple_add(self):
        o = self.ctx.DataObject(ident=R.URIRef("http://example.org/a"))
        DataObject.DatatypeProperty("boots", o)
        o.boots()
        c1 = o.po_cache
        self.assertIsNotNone(c1)
        self.config['rdf.graph'].add((R.URIRef('http://example.org/a'),
                                      R.URIRef('http://bluhbluh.com'),
                                      R.URIRef('http://bluhah.com')))
        o.boots()
        self.assertIsNot(c1, o.po_cache)

    def test_cache_no_refresh_for_no_change(self):
        o = self.ctx.DataObject(ident=R.URIRef("http://example.org/a"))
        DataObject.DatatypeProperty("boots", o)
        o.boots()
        c1 = o.po_cache
        self.assertIsNotNone(c1)
        o.boots()
        self.assertIs(c1, o.po_cache)

    def test_cache_refresh_after_triple_remove(self):
        o = self.ctx.DataObject(ident=R.URIRef("http://example.org/a"))
        DataObject.DatatypeProperty("boots", o)
        o.boots()
        c1 = o.po_cache
        self.assertIsNotNone(c1)
        # XXX: Note that it doesn't matter if the triple was
        # actually in the graph
        self.config['rdf.graph'].remove((R.URIRef('/not/in'),
                                         R.URIRef('/the'),
                                         R.URIRef('/graph')))
        o.boots()
        self.assertIsNot(c1, o.po_cache)

    def test_cache_refresh_clear(self):
        o = self.ctx.DataObject(ident=R.URIRef("http://example.org/a"))
        DataObject.DatatypeProperty("boots", o)
        o.boots()
        c1 = o.po_cache
        self.assertIsNotNone(c1)
        # XXX: Note that it doesn't matter if the triple was
        # actually in the graph
        o.clear_po_cache()
        o.boots()
        self.assertIsNot(c1, o.po_cache)
