from PyOpenWorm.json_schema import (Creator,
                                    AssignmentValidationException)
import unittest


class DefaultTest(unittest.TestCase):
    '''
    Tests for setting the value from the "default" member.
    '''
    def test(self):
        expected = 'DEFAULT'
        cut = Creator({
            'default': expected,
            'type': 'string'
        })

        self.assertEqual(expected, cut.create(None))


class TypeCheckTest(unittest.TestCase):
    '''
    Check type checking for primitive types
    '''
    def test_string(self):
        expected = 'EXPECTED'
        cut = Creator({
            'type': 'string'
        })

        self.assertEqual(expected, cut.create(expected))

    def test_string_wrong_type_error(self):
        cut = Creator({
            'type': 'does_not_matter'
        })

        with self.assertRaises(AssignmentValidationException):
            cut.create('VALUE')

    def test_number_given_int(self):
        cut = Creator({
            'type': 'number'
        })

        self.assertEqual(1, cut.create(1))

    def test_number_given_float(self):
        cut = Creator({
            'type': 'number'
        })

        self.assertEqual(2.2, cut.create(2.2))

    def test_integer_given_float_error(self):
        cut = Creator({
            'type': 'integer'
        })

        with self.assertRaises(AssignmentValidationException):
            cut.create(2.2)

    def test_integer_given_int(self):
        cut = Creator({
            'type': 'integer'
        })

        self.assertEqual(5, cut.create(5))


class BooleanTypeCheckTest(unittest.TestCase):

    def test_true(self):
        cut = Creator({
            'type': 'boolean'
        })

        self.assertEqual(True, cut.create(True))

    def test_false(self):
        cut = Creator({
            'type': 'boolean'
        })

        self.assertEqual(False, cut.create(False))

    def test_wrong_type_error(self):
        cut = Creator({
            'type': 'boolean'
        })

        with self.assertRaises(AssignmentValidationException):
            cut.create('blah blah')


class ArrayTypeCheckTest(unittest.TestCase):
    def test_no_items(self):
        cut = Creator({
            'type': 'array'
        })

        val = ['blah', 2, 2.3, True]
        self.assertEqual(val, cut.create(val))

    def test_items(self):
        cut = Creator({
            'type': 'array',
            'items': {'type': 'string'}
        })

        with self.assertRaises(AssignmentValidationException):
            cut.create(['blah', True])


class DictTypeCheckTest(unittest.TestCase):
    def test_no_items(self):
        cut = Creator({
            'type': 'array'
        })

        val = ['blah', 2, 2.3, True]
        self.assertEqual(val, cut.create(val))

    def test_items(self):
        cut = Creator({
            'type': 'array',
            'items': {'type': 'string'}
        })

        with self.assertRaises(AssignmentValidationException):
            cut.create(['blah', True])

    def test_items_empty(self):
        cut = Creator({
            'type': 'array',
            'items': {'type': 'string'}
        })

        self.assertEqual([], cut.create([]))


class ObjectTypeCheck(unittest.TestCase):
    def test_no_pow_type(self):
        cut = Creator({
            'type': 'object',
        })

        with self.assertRaises(AssignmentValidationException):
            cut.create({})

    def test_make_instance(self):
        class A(object):
            pass

        class C(Creator):
            def make_instance(self, pow_type):
                return A()

        cut = C({
            'type': 'object',
            '_pow_type': 'whatever'
        })
        self.assertIsInstance(cut.create({}), A)

    def test_assign(self):
        class A(object):
            pass

        called = [False]

        class C(Creator):
            def make_instance(self, pt):
                return A()

            def assign(self, obj, name, val):
                called[0] = True

        cut = C({
            'type': 'object',
            '_pow_type': 'whatever'
        })
        cut.create({'duck': 'sauce'})
        self.assertTrue(called[0])

    def test_additionalProperties(self):
        pass

    def test_patternProperties(self):
        pass

    def test_properties(self):
        pass
