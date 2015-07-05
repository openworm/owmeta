import sys
sys.path.insert(0,".")
from PyOpenWorm import DataObject, SimpleProperty
import rdflib as R

from DataTestTemplate import _DataTest

class SimplePropertyTest(_DataTest):
    def __init__(self,*args,**kwargs):
        _DataTest.__init__(self,*args,**kwargs)

        class K(DataObject):
            def __init__(self):
                K.DatatypeProperty('boots', self)
                K.ObjectProperty('bats', self)
        self.k = K

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

    def test_non_multiple_saves_single_values(self):
        class C(DataObject):
            datatypeProperties = [{'name':'t', 'multiple':False}]
        do = C(key="s")
        do.t("value1")
        do.t("vaule2")
        do.save()

        do1 = C(key="s")
        self.assertEqual(len(list(do1.t.get())), 1)

    def test_unset_single(self):
        boots = self.k().boots

        boots.set("l")
        boots.unset("l")
        self.assertEqual(len(boots.values), 0)

    def test_unset_single_property_value(self):
        from PyOpenWorm.dataObject import PropertyValue
        boots = self.k().boots

        boots.set("l")
        boots.unset(PropertyValue("l"))
        self.assertEqual(len(boots.values), 0)

    def test_unset_single_by_identifier(self):
        bats = self.k().bats

        o = self.k(key='blah')
        bats.set(o)
        bats.unset(o.identifier())
        self.assertEqual(len(bats.values), 0)

    def test_unset_multiple(self):
        bets = self.k().bets
        bets.set("l")
        bets.unset("l")
        self.assertEqual(len(bets.values), 0)

    def test_unset_empty(self):
        """ Attempting to unset a value that isn't set should raise an error """
        bits = self.k().bits
        with self.assertRaises(Exception):
            bits.unset("random")

    def test_unset_wrong_value(self):
        """ Attempting to unset a value that isn't set should raise an error """
        bits = self.k().bits
        bits.set(self.k(key='roger'))
        with self.assertRaises(Exception):
            bits.unset("random")
