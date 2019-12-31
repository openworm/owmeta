import unittest

try:
    from unittest.mock import patch, Mock
except ImportError:
    from mock import patch, Mock

from pytest import mark
from owmeta.command_util import SubCommand, IVar
from owmeta.cli_command_wrapper import CLICommandWrapper
import owmeta.cli as PCLI
from .TestUtilities import noexit, stderr, stdout
import json
import re


class CLICommandWrapperTest(unittest.TestCase):

    def test_method_sc(self):
        class A(object):
            def __init__(self):
                self.i = 0

            def sc(self):
                self.i += 1
        a = A()
        cm = CLICommandWrapper(a)
        parser = cm.parser()
        parser.parse_args(['sc'])
        cm.mapper.apply(a)
        self.assertEqual(a.i, 1)

    def test_method_sc_doc(self):
        class A(object):
            def __init__(self):
                self.i = 0

            def sc(self):
                ''' TEST_STRING '''
                self.i += 1
        a = A()
        cm = CLICommandWrapper(a)
        parser = cm.parser()
        self.assertIn('TEST_STRING', parser.format_help())

    def test_method_sc_doc_param(self):
        class A(object):
            def __init__(self):
                self.i = 0

            def sc(self, opt):
                '''
                Test

                Parameters
                ----------
                opt : str
                    TEST_STRING
                '''
                self.i += 1
        a = A()
        cm = CLICommandWrapper(a)
        parser = cm.parser()
        with noexit(), stdout() as out:
            parser.parse_args(['sc', '--help'])
        self.assertIn('TEST_STRING', out.getvalue())

    def test_method_sc_nargs(self):
        class A(object):
            def __init__(self):
                self.i = 0

            def sc(self, opt):
                '''
                Test

                Parameters
                ----------
                *opt : str
                    _
                '''
                self.i += 1
        a = A()
        cm = CLICommandWrapper(a)
        parser = cm.parser()
        with noexit(), stdout() as out:
            parser.parse_args(['sc', '--help'])
        self.assertIn('opt ...', out.getvalue())

    def test_subcommand_sc(self):
        class S(object):
            def __init__(self, parent):
                self._parent = parent

            def __call__(self):
                self._parent.i = 1

        class A(object):
            def __init__(self):
                self.i = 0
            sc = SubCommand(S)

        a = A()
        cm = CLICommandWrapper(a)
        parser = cm.parser()
        parser.parse_args(['sc'])
        cm.mapper.apply(a)

        self.assertEqual(a.i, 1)

    def test_ivar_default_str(self):
        class A(object):
            p = IVar(3)
        a = A()
        cm = CLICommandWrapper(a)
        parser = cm.parser()
        with noexit(), stdout() as out:
            parser.parse_args(['sc', '--help'])
        self.assertIn('3', out.getvalue())

    def test_ivar_default_append(self):
        class A(object):
            p = IVar(3, doc='TEST_STRING')
        a = A()
        cm = CLICommandWrapper(a)
        parser = cm.parser()
        with noexit(), stdout() as out:
            parser.parse_args(['sc', '--help'])
        self.assertIn('3', out.getvalue())

    def test_ivar_default_append_doc(self):
        class A(object):
            p = IVar(3, doc='TEST_STRING')
        a = A()
        cm = CLICommandWrapper(a)
        parser = cm.parser()
        with noexit(), stdout() as out:
            parser.parse_args(['sc', '--help'])
        self.assertIn('TEST_STRING', out.getvalue())


class CLIOutputModeTest(unittest.TestCase):
    def setUp(self):
        self.ccw = patch('owmeta.cli.CLICommandWrapper').start()
        patch('owmeta.cli.OWM').start()
        patch('owmeta.cli.GitRepoProvider').start()

    def tearDown(self):
        patch.stopall()


class CLIJSONOutputModeTest(CLIOutputModeTest):
    def test_json_list(self):
        with noexit(), stdout() as so:
            @with_defaults
            def main(argument_namespace_callback, **kwargs):
                argument_namespace_callback.output_mode = 'json'
                return ['a']
            self.ccw().main.side_effect = main
            PCLI.main()
        self.assertEqual(json.loads(so.getvalue()), ['a'])

    def test_json_set(self):
        with noexit(), stdout() as so:
            @with_defaults
            def main(argument_namespace_callback, **kwargs):
                argument_namespace_callback.output_mode = 'json'
                return set('ab')
            self.ccw().main.side_effect = main
            PCLI.main()
        val = json.loads(so.getvalue())
        self.assertTrue(val == list('ba') or val == list('ab'))

    def test_json_context(self):
        with noexit(), stdout() as so:
            @with_defaults
            def main(argument_namespace_callback, **kwargs):
                from owmeta.context import Context
                argument_namespace_callback.output_mode = 'json'
                return Context('ident', base_namespace='base_namespace')
            self.ccw().main.side_effect = main
            PCLI.main()
        val = json.loads(so.getvalue())
        self.assertEqual(val, dict(identifier='ident', base_namespace='base_namespace'))

    def test_json_graph(self):
        with noexit(), stdout() as so:
            @with_defaults
            def main(argument_namespace_callback, **kwargs):
                from rdflib.graph import Graph
                argument_namespace_callback.output_mode = 'json'
                return Mock(name='graph', spec=Graph())
            self.ccw().main.side_effect = main
            PCLI.main()
        val = json.loads(so.getvalue())
        self.assertEqual(val, [])


class CLITextOutputModeTest(CLIOutputModeTest):
    def test_text_list(self):
        with noexit(), stdout() as so:
            @with_defaults
            def main(argument_namespace_callback, **kwargs):
                argument_namespace_callback.output_mode = 'text'
                return ['a']
            self.ccw().main.side_effect = main
            PCLI.main()
        self.assertEqual(so.getvalue(), 'a\n')

    def test_text_multiple_element_list(self):
        with noexit(), stdout() as so:
            @with_defaults
            def main(argument_namespace_callback, **kwargs):
                argument_namespace_callback.output_mode = 'text'
                return ['a', 'b']
            self.ccw().main.side_effect = main
            PCLI.main()
        self.assertEqual(so.getvalue(), 'a\nb\n')

    def test_text_set(self):
        with noexit(), stdout() as so:
            @with_defaults
            def main(argument_namespace_callback, **kwargs):
                argument_namespace_callback.output_mode = 'text'
                return set('ab')
            self.ccw().main.side_effect = main
            PCLI.main()
        self.assertTrue(so.getvalue() == 'b\na\n' or so.getvalue() == 'a\nb\n')

    def test_text_dict(self):
        with noexit(), stdout() as so:

            @with_defaults
            def main(argument_namespace_callback, **kwargs):
                argument_namespace_callback.output_mode = 'text'
                return dict(a='b')
            self.ccw().main.side_effect = main
            PCLI.main()
        self.assertEqual(so.getvalue(), 'a\tb\n')

    def test_text_dict_field_separator(self):
        with noexit(), stdout() as so:
            @with_defaults
            def main(argument_namespace_callback, **kwargs):
                argument_namespace_callback.output_mode = 'text'
                argument_namespace_callback.text_field_separator = '\0'
                return dict(a='b')
            self.ccw().main.side_effect = main
            PCLI.main()
        self.assertEqual(so.getvalue(), 'a\0b\n')

    def test_text_dict_record_separator(self):
        with noexit(), stdout() as so:
            @with_defaults
            def main(argument_namespace_callback, **kwargs):
                argument_namespace_callback.output_mode = 'text'
                argument_namespace_callback.text_record_separator = '\0'
                return dict(a='b')
            self.ccw().main.side_effect = main
            PCLI.main()
        self.assertEqual(so.getvalue(), 'a\tb\0')

    def test_text_list_record_separator(self):
        with noexit(), stdout() as so:
            @with_defaults
            def main(argument_namespace_callback, **kwargs):
                argument_namespace_callback.output_mode = 'text'
                argument_namespace_callback.text_record_separator = '\0'
                return ['a', 'b']
            self.ccw().main.side_effect = main
            PCLI.main()
        self.assertEqual(so.getvalue(), 'a\0b\0')

    def test_text_uniterable(self):
        target = object()
        with noexit(), stdout() as so:
            @with_defaults
            def main(argument_namespace_callback, **kwargs):
                argument_namespace_callback.output_mode = 'text'
                return target
            self.ccw().main.side_effect = main
            PCLI.main()
        self.assertEqual(so.getvalue(), str(target) + '\n')

    def test_text_iterable_type_error(self):
        with noexit(), stdout() as so:
            @with_defaults
            def main(argument_namespace_callback, **kwargs):
                argument_namespace_callback.output_mode = 'text'

                def iterable():
                    yield 'blah'
                    yield 'blah'
                    raise TypeError("blah blah")
                return iterable()
            self.ccw().main.side_effect = main
            with self.assertRaises(TypeError):
                PCLI.main()
            self.assertEqual(so.getvalue(), 'blah\nblah\n')


class CLITableOutputModeTest(CLIOutputModeTest):
    def test_no_headers_or_columns_header_name(self):
        with noexit(), stdout() as so:
            @with_defaults
            def main(argument_namespace_callback, **kwargs):
                argument_namespace_callback.output_mode = 'table'

                def iterable():
                    yield 'blah'
                    yield 'blah'
                return iterable()
            self.ccw().main.side_effect = main
            PCLI.main()
            self.assertRegexpMatches(so.getvalue(), 'Value')

    def test_no_headers_or_columns_row_value(self):
        with noexit(), stdout() as so:
            @with_defaults
            def main(argument_namespace_callback, **kwargs):
                argument_namespace_callback.output_mode = 'table'

                def iterable():
                    yield 'blah'
                    yield 'blah'
                return iterable()
            self.ccw().main.side_effect = main
            PCLI.main()
            self.assertRegexpMatches(so.getvalue(), 'blah')

    def test_with_header_row(self):
        with noexit(), stdout() as so:
            @with_defaults
            def main(argument_namespace_callback, **kwargs):
                argument_namespace_callback.output_mode = 'table'

                def gen():
                    yield 'blah'
                    yield 'blah'
                it = gen()

                class Iterable(object):
                    header = ['FIELD']

                    def __next__(self):
                        return next(it)

                    next = __next__

                    def __iter__(self):
                        return iter(it)

                return Iterable()
            self.ccw().main.side_effect = main
            PCLI.main()
            self.assertRegexpMatches(so.getvalue(), 'blah')

    def test_with_header_name(self):
        with noexit(), stdout() as so:
            @with_defaults
            def main(argument_namespace_callback, **kwargs):
                argument_namespace_callback.output_mode = 'table'

                def gen():
                    yield 'blah'
                    yield 'blah'
                it = gen()

                class Iterable(object):
                    header = ['FIELD']

                    def __next__(self):
                        return next(it)

                    next = __next__

                    def __iter__(self):
                        return iter(it)

                return Iterable()
            self.ccw().main.side_effect = main
            PCLI.main()
            self.assertRegexpMatches(so.getvalue(), 'FIELD')

    def test_with_header_and_columns_accessor(self):
        with noexit(), stdout() as so:
            @with_defaults
            def main(argument_namespace_callback, **kwargs):
                argument_namespace_callback.output_mode = 'table'

                def gen():
                    yield 'blah'
                    yield 'blah'
                it = gen()

                class Iterable(object):
                    header = ['FIELD']
                    columns = [lambda x: x[:1]]

                    def __next__(self):
                        return next(it)

                    next = __next__

                    def __iter__(self):
                        return iter(it)

                return Iterable()
            self.ccw().main.side_effect = main
            PCLI.main()
            self.assertRegexpMatches(so.getvalue(), re.compile('^b *$', flags=re.MULTILINE))


def with_defaults(func):
    '''
    Sets the default values for options
    '''
    from functools import wraps

    @wraps(func)
    def wrapper(argument_namespace_callback, argument_callback, *args, **kwargs):
        collect_argument_defaults(argument_namespace_callback, argument_callback)
        kwargs['argument_namespace_callback'] = argument_namespace_callback
        kwargs['argument_callback'] = argument_callback
        return func(*args, **kwargs)
    return wrapper


def collect_argument_defaults(ns, callback):
    res = dict()
    parser = Mock(name='parser')

    def cb(*args, **kwargs):
        da = kwargs.get('default')
        setattr(ns, args[0].strip('-').replace('-', '_'), da)
    parser.add_argument.side_effect = cb
    callback(parser)
    return res
