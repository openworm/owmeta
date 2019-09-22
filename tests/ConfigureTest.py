from __future__ import absolute_import
from __future__ import print_function
import tempfile
import unittest
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch
from owmeta.configure import Configure, ConfigValue, Configureable
from owmeta.data import Data
import os


class ConfigureTest(unittest.TestCase):
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
        self.assertEqual("sign", c['seven'])

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
        a = {'t': False}

        class pipe(ConfigValue):
            def get(self):
                a['t'] = True
                return "sign"
        c['seven'] = pipe()
        self.assertFalse(a['t'])
        self.assertEqual(c['seven'], "sign")
        self.assertTrue(a['t'])

    def test_read_from_file_success(self):
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

    def test_read_from_file_env_val_success(self):
        with patch.dict('os.environ', {'ENV_VAR': 'myapikey'}):
            tf = self.tempfile()
            print('{"z": "$ENV_VAR"}', file=tf)
            tf.close()
            try:
                c = Configure.open(tf.name)
                self.assertEqual(c['z'], 'myapikey')
            finally:
                os.unlink(tf.name)

    def test_read_from_file_env_val_fail_name_1(self):
        tf = self.tempfile()
        print('{"z": "$1"}', file=tf)
        tf.close()
        try:
            with self.assertRaises(ValueError):
                Configure.open(tf.name)
        finally:
            os.unlink(tf.name)

    def test_read_from_file_env_val_fail_name_2(self):
        tf = self.tempfile()
        print('{"z": "$1StillNoGood"}', file=tf)
        tf.close()
        try:
            with self.assertRaises(ValueError):
                Configure.open(tf.name)
        finally:
            os.unlink(tf.name)

    def test_read_from_file_env_val_no_recurse(self):
        with patch.dict('os.environ', {'ENV_VAR': 'myapikey', "ENV_VAR1": "$ENV_VAR"}):
            tf = self.tempfile()
            print('{"z": "$ENV_VAR1"}', file=tf)
            tf.close()
            try:
                c = Configure.open(tf.name)
                self.assertEqual(c['z'], '$ENV_VAR')
            finally:
                os.unlink(tf.name)

    def test_read_from_file_env_val_empty_string(self):
        with patch.dict('os.environ', {'ENV_VAR': ''}):
            tf = self.tempfile()
            print('{"z": "$ENV_VAR"}', file=tf)
            tf.close()
            try:
                c = Configure.open(tf.name)
                self.assertIsNone(c['z'])
            finally:
                os.unlink(tf.name)

    def test_read_from_file_env_val_not_defined(self):
        with patch.dict('os.environ', (), clear=True):
            tf = self.tempfile()
            print('{"z": "$ENV_VAR"}', file=tf)
            tf.close()
            try:
                c = Configure.open(tf.name)
                self.assertIsNone(c['z'])
            finally:
                os.unlink(tf.name)

    def test_read_from_file_env_val_embedded_success(self):
        with patch.dict('os.environ', {'USER': 'dave'}, clear=True):
            tf = self.tempfile()
            print('{"greeting": "Hello, $USER"}', file=tf)
            tf.close()
            try:
                c = Configure.open(tf.name)
                self.assertEqual(c['greeting'], 'Hello, dave')
            finally:
                os.unlink(tf.name)

    def test_read_from_file_env_val_multi_embedded_success(self):
        with patch.dict('os.environ', {'USER': 'dave', 'IS_SUPER': 'normal'}, clear=True):
            tf = self.tempfile()
            print('{"greeting": "Hello, $IS_SUPER $USER"}', file=tf)
            tf.close()
            try:
                c = Configure.open(tf.name)
                self.assertEqual(c['greeting'], 'Hello, normal dave')
            finally:
                os.unlink(tf.name)

    def test_read_from_file_env_val_multi_empty(self):
        with patch.dict('os.environ', (), clear=True):
            tf = self.tempfile()
            print('{"z": "$V1$V2"}', file=tf)
            tf.close()
            try:
                c = Configure.open(tf.name)
                self.assertIsNone(c['z'])
            finally:
                os.unlink(tf.name)

    def test_base_varname(self):
        with patch('owmeta.configure.resource_filename') as rf:
            with patch.dict('os.environ', (), clear=True):
                rf.return_value = 'moosh'
                tf = self.tempfile()
                print('{"z": "$BASE/car"}', file=tf)
                tf.close()
                try:
                    c = Configure.open(tf.name)
                    self.assertEqual(c['z'], 'moosh/car')
                finally:
                    os.unlink(tf.name)

    def test_base_varname_override(self):
        with patch('owmeta.configure.resource_filename') as rf:
            with patch.dict('os.environ', {'BASE': 'cars'}, clear=True):
                rf.return_value = 'moosh'
                tf = self.tempfile()
                print('{"z": "$BASE/car"}', file=tf)
                tf.close()
                try:
                    c = Configure.open(tf.name)
                    self.assertEqual(c['z'], 'cars/car')
                finally:
                    os.unlink(tf.name)

    def test_here_varname(self):
        '''
        By default, $HERE refers to the directory the config file sits in, or to the
        current working directory
        '''
        with patch.dict('os.environ', (), clear=True):
            tf = self.tempfile()
            dname = os.path.dirname(tf.name)
            print('{"z": "$HERE/car"}', file=tf)
            tf.close()
            try:
                c = Configure.open(tf.name)
                self.assertEqual(c['z'], dname + '/car')
            finally:
                os.unlink(tf.name)

    def test_here_varname_root(self):
        with patch.dict('os.environ', (), clear=True):
            c = Configure.process_config({'configure.file_location': '/blah.file',
                                          'z': '$HERE/car'})
            self.assertEqual(c['z'], '/car')

    def test_here_varname_override(self):
        with patch.dict('os.environ', {'HERE': 'there'}, clear=True):
            c = Configure.process_config({'configure.file_location': '/blah.file',
                                          'z': '$HERE/car'})
            self.assertEqual(c['z'], 'there/car')

    def test_here_varname_no_value(self):
        with patch.dict('os.environ', (), clear=True):
            c = Configure.process_config({'z': '$HERE/car'})
            self.assertEqual(c['z'], '/car')

    def test_copy_dict(self):
        c = Configure()
        c.copy({'a': 1})
        self.assertEqual(c['a'], 1)

    def test_copy_non_string_key(self):
        c = Configure()
        c.copy({5: 1})
        self.assertEqual(c[5], 1)

    def test_configurable_init_empty(self):
        """Ensure Configureable gets init'd with the defalut if nothing is given"""
        i = Configureable()
        self.assertEqual(Configureable.default, i.conf)

    def test_configurable_init_False(self):
        """Ensure Configureable gets init'd with the defalut if None is given"""
        i = Configureable(conf=None)
        self.assertEqual(Configureable.default, i.conf)

    def test_dict_init(self):
        c = Configure(x=4, y=3)
        self.assertEqual(4, c['x'])

    def test_iter(self):
        c = Configure(x=2, y=1)
        self.assertEqual({'x', 'y'}, {s for s in c})

    def test_contains(self):
        c = Configure(x=2, y=1)
        self.assertIn('x', c)

    @staticmethod
    def tempfile():
        return tempfile.NamedTemporaryFile(mode='w+', delete=False)
