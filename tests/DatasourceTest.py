from __future__ import absolute_import
from __future__ import print_function
import unittest
from PyOpenWorm.datasource import Informational, DataSource, DuplicateAlsoException


class InformationalTest(unittest.TestCase):

    def test_default_property_type(self):
        inf = Informational()
        self.assertEqual(inf.property_type, 'DatatypeProperty')

    def test_default_multiple(self):
        inf = Informational()
        self.assertTrue(inf.multiple)

    def test_default_display_name(self):
        inf = Informational(name='test')
        self.assertEqual(inf.display_name, 'test')


class DataSourceTest(unittest.TestCase):
    def setUp(self):
        class DS1(DataSource):
            a = Informational(default_value='A')

        class DS2(DS1):
            b = Informational()
            a = 'D'
        self.DS1 = DS1
        self.DS2 = DS2

    def test_subclass_class_assignment_1(self):
        ds1 = self.DS1()
        ds2 = self.DS2()
        self.assertNotEqual(ds1.a.onedef(), ds2.a.onedef())

    def test_subclass_class_assignment_2(self):
        ds1 = self.DS1()
        ds2 = self.DS2()
        self.assertNotEqual(ds1.a.defined_values, ds2.a.defined_values)

    def test_subclass_class_assignment_3(self):
        ds1 = self.DS1()
        ds2 = self.DS2()
        self.assertNotEqual(ds1.a, ds2.a)

    def test_subclass_class_assignment_4(self):
        ds1 = self.DS1()
        ds2 = self.DS2()
        self.assertIsNot(ds1.a, ds2.a)

    def test_subclass_class_assignment_5(self):
        ds1 = self.DS1()
        ds2 = self.DS2()
        self.assertIsNot(ds1, ds2)

    def test_subclass_class_info_fields_1(self):
        self.assertNotEqual(self.DS1.info_fields, self.DS2.info_fields)

    def test_subclass_class_info_fields_2(self):
        self.assertEqual(len(self.DS1.info_fields), 4,
                         msg='should have translation, source, and "a"')

    def test_subclass_class_info_fields_3(self):
        self.assertEqual(len(self.DS2.info_fields), 5,
                         msg='should have translation, source, and "a" and "b"')

    def test_also(self):
        class C(self.DS1):
            q = Informational(also=self.DS1.a)
        c = C(q='Q')
        self.assertEqual(c.a.onedef(), 'Q')

    def test_also_dup_no_error_1(self):
        """
        No error when only one 'also'-setter has a default value, but the
        setter values should be set
        """
        class C(self.DS1):
            q = Informational(also=self.DS1.a, default_value='Q')
            p = Informational(also=self.DS1.a)
        c = C()
        self.assertEqual(c.a.onedef(), 'Q')

    def test_also_dup_no_error_2(self):
        """ Should not see any error when there's no value set """
        class C(self.DS1):
            q = Informational(also=self.DS1.a)
            p = Informational(also=self.DS1.a)
        c = C()
        self.assertEqual(c.a.onedef(), 'A')

    def test_also_dup_no_error_3(self):
        """ No error when the values are set the same """
        class C(self.DS1):
            q = Informational(also=self.DS1.a, default_value='R')
            p = Informational(also=self.DS1.a, default_value='R')
        c = C()
        self.assertEqual(c.a.onedef(), 'R')

    def test_also_dup_no_error_4(self):
        """
        No error when the values are set the same, even if the values are set
        from different places
        """
        class C(self.DS1):
            q = Informational(also=self.DS1.a)
            p = Informational(also=self.DS1.a, default_value='R')
        c = C(q='R')
        self.assertEqual(c.a.onedef(), 'R')

    def test_also_dup_no_error_5(self):
        """
        No error when the values are set the same, even if the values are set
        from different places
        """
        class C(self.DS1):
            q = Informational(also=self.DS1.a)
            p = Informational(also=self.DS1.a)
        c = C(q='R', p='R')
        self.assertEqual(c.a.onedef(), 'R')

    def test_also_overriden_by_explicit_1(self):
        class C(self.DS1):
            q = Informational(also=self.DS1.a)
        c = C(a='M', q='R')
        self.assertEqual(c.a.onedef(), 'M')

    def test_also_overriden_by_explicit_2(self):
        class C(self.DS1):
            q = Informational(also=self.DS1.a, default_value='R')
        c = C(a='M')
        self.assertEqual(c.a.onedef(), 'M')

    def test_also_overriden_by_explicit_3(self):
        class C(self.DS1):
            q = Informational(also=self.DS1.a, default_value='R')
            a = 'M'
        c = C()
        self.assertEqual(c.a.onedef(), 'M')

    def test_also_overrides_explicit_None(self):
        class C(self.DS1):
            q = Informational(also=self.DS1.a, default_value='R')
        c = C(a=None)
        self.assertEqual(c.a.onedef(), 'R')

    def test_also_default_override(self):
        class C(self.DS1):
            q = Informational(also=self.DS1.a, default_value='Q')
        c = C()
        self.assertEqual(c.a.onedef(), 'Q')
