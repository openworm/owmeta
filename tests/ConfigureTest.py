from __future__ import absolute_import
import unittest
from PyOpenWorm.configure import Configure, ConfigValue, Configureable
from PyOpenWorm.data import Data


class ConfigureTest(unittest.TestCase):
    """
    Tests for the Configure class, which provides
      functionality to modules to allow outside objects to parameterize their
      behavior
    """
    def test_fake_config(self):
        """ Try to retrieve a config value that hasn't been set """
        with self.assertRaises(KeyError):
            c = Configure()
            c['not_a_valid_config']

    def test_literal(self):
        """ Assign a literal rather than a ConfigValue"""
        c = Configure()
        c['seven'] = "coke"
        self.assertEqual(c['seven'], "coke")

    def test_ConfigValue(self):
        """ Assign a ConfigValue"""
        c = Configure()
        class pipe(ConfigValue):
            def get(self):
                return "sign"
        c['seven'] = pipe()
        self.assertEqual("sign",c['seven'])

    def test_getter_no_ConfigValue(self):
        """ Assign a method with a "get". Should return a the object rather than calling its get method """
        c = Configure()
        class pipe:
            def get(self):
                return "sign"
        c['seven'] = pipe()
        self.assertIsInstance(c['seven'], pipe)

    def test_late_get(self):
        """ "get" shouldn't be called until the value is *dereferenced* """
        c = Configure()
        a = {'t' : False}
        class pipe(ConfigValue):
            def get(self):
                a['t'] = True
                return "sign"
        c['seven'] = pipe()
        self.assertFalse(a['t'])
        self.assertEqual(c['seven'], "sign")
        self.assertTrue(a['t'])

    def test_read_from_file(self):
        """ Read configuration from a JSON file """
        try:
            d = Data.open("tests/test.conf")
            self.assertEqual("test_value", d["test_variable"])
        except Exception:
            self.fail("test.conf should exist and be valid JSON")

    def test_read_from_file_fail(self):
        """ Fail on attempt to read configuration from a non-JSON file """
        with self.assertRaises(ValueError):
            Data.open("tests/test_data/bad_test.conf")

    def test_configurable_init_empty(self):
        """Ensure Configureable gets init'd with the defalut if nothing is given"""
        i = Configureable()
        self.assertEqual(Configureable.conf, i.conf)

    def test_configurable_init_False(self):
        """Ensure Configureable gets init'd with the defalut if None is given"""
        i = Configureable(conf=None)
        self.assertEqual(Configureable.conf, i.conf)

    def test_dict_init(self):
        c = Configure(x=4, y=3)
        self.assertEqual(4, c['x'])
