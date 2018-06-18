import unittest
try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock

from PyOpenWorm.identifier_mixin import IdMixin


class IdentifierMixinTest(unittest.TestCase):

    def setUp(self):
        class A(IdMixin()):
            rdf_namespace = MagicMock()

        self.cls = A

    def test_identifier_with_key(self):
        a = self.cls()
        a.key = 'blah'
        self.assertIsNotNone(a.identifier)

    def test_defined_with_key(self):
        a = self.cls()
        a.key = 'blah'
        self.assertTrue(a.defined)

    def test_defined_with_key_init(self):
        a = self.cls(key='blah')
        self.assertTrue(a.defined)

    def test_identifier_with_key_init(self):
        a = self.cls(key='blah')
        self.assertIsNotNone(a.identifier)

    def test_namespace_key_error(self):
        def s(*args):
            raise KeyError()
        self.cls.rdf_namespace.__getitem__.side_effect = s
        with self.assertRaises(KeyError, message='KeyError should flow up'):
            self.cls(key='blah')
