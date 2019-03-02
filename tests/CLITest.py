import unittest

try:
    from unittest.mock import patch, Mock
except ImportError:
    from mock import patch, Mock

from pytest import mark
from PyOpenWorm.command_util import SubCommand, IVar
from PyOpenWorm.cli_command_wrapper import CLICommandWrapper
import PyOpenWorm.cli as PCLI
from .TestUtilities import noexit, stderr, stdout
import json


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


class CLITestOutputMode(unittest.TestCase):
    def test_json_list(self):
        with patch('PyOpenWorm.cli.CLICommandWrapper') as ccw, \
                noexit(), stdout() as so:

            @with_defaults
            def main(argument_namespace_callback, **kwargs):
                argument_namespace_callback.output_mode = 'json'
                return ['a']
            ccw().main.side_effect = main
            PCLI.main()
        self.assertEqual(json.loads(so.getvalue()), ['a'])

    def test_json_set(self):
        with patch('PyOpenWorm.cli.CLICommandWrapper') as ccw, \
                noexit(), stdout() as so:

            @with_defaults
            def main(argument_namespace_callback, **kwargs):
                argument_namespace_callback.output_mode = 'json'
                return set('ab')
            ccw().main.side_effect = main
            PCLI.main()
        val = json.loads(so.getvalue())
        self.assertTrue(val == list('ba') or val == list('ab'))

    def test_json_context(self):
        with patch('PyOpenWorm.cli.CLICommandWrapper') as ccw, \
                noexit(), stdout() as so:

            @with_defaults
            def main(argument_namespace_callback, **kwargs):
                from PyOpenWorm.context import Context
                argument_namespace_callback.output_mode = 'json'
                m = Mock(name='context_result', spec=Context())
                m.identifier = 'ident'
                m.base_namespace = 'base_namespace'
                return m
            ccw().main.side_effect = main
            PCLI.main()
        val = json.loads(so.getvalue())
        self.assertEqual(val, dict(identifier='ident', base_namespace='base_namespace'))

    def test_json_graph(self):
        with patch('PyOpenWorm.cli.CLICommandWrapper') as ccw, \
                noexit(), stdout() as so:

            @with_defaults
            def main(argument_namespace_callback, **kwargs):
                from rdflib.graph import Graph
                argument_namespace_callback.output_mode = 'json'
                return Mock(name='graph', spec=Graph())
            ccw().main.side_effect = main
            PCLI.main()
        val = json.loads(so.getvalue())
        self.assertEqual(val, [])

    def test_text_list(self):
        with patch('PyOpenWorm.cli.CLICommandWrapper') as ccw, \
                noexit(), stdout() as so:

            @with_defaults
            def main(argument_namespace_callback, **kwargs):
                argument_namespace_callback.output_mode = 'text'
                return ['a']
            ccw().main.side_effect = main
            PCLI.main()
        self.assertEqual(so.getvalue(), 'a\n')

    def test_text_multiple_element_list(self):
        with patch('PyOpenWorm.cli.CLICommandWrapper') as ccw, \
                noexit(), stdout() as so:

            @with_defaults
            def main(argument_namespace_callback, **kwargs):
                argument_namespace_callback.output_mode = 'text'
                return ['a', 'b']
            ccw().main.side_effect = main
            PCLI.main()
        self.assertEqual(so.getvalue(), 'a\nb\n')

    def test_text_set(self):
        with patch('PyOpenWorm.cli.CLICommandWrapper') as ccw, \
                noexit(), stdout() as so:

            @with_defaults
            def main(argument_namespace_callback, **kwargs):
                argument_namespace_callback.output_mode = 'text'
                return set('ab')
            ccw().main.side_effect = main
            PCLI.main()
        self.assertTrue(so.getvalue() == 'b\na\n' or so.getvalue() == 'a\nb\n')

    def test_text_dict(self):
        with patch('PyOpenWorm.cli.CLICommandWrapper') as ccw, \
                noexit(), stdout() as so:

            @with_defaults
            def main(argument_namespace_callback, **kwargs):
                argument_namespace_callback.output_mode = 'text'
                return dict(a='b')
            ccw().main.side_effect = main
            PCLI.main()
        self.assertEqual(so.getvalue(), 'a\tb\n')

    def test_text_dict_field_separator(self):
        with patch('PyOpenWorm.cli.CLICommandWrapper') as ccw, \
                noexit(), stdout() as so:

            @with_defaults
            def main(argument_namespace_callback, **kwargs):
                argument_namespace_callback.output_mode = 'text'
                argument_namespace_callback.text_field_separator = '\0'
                return dict(a='b')
            ccw().main.side_effect = main
            PCLI.main()
        self.assertEqual(so.getvalue(), 'a\0b\n')

    def test_text_dict_record_separator(self):
        with patch('PyOpenWorm.cli.CLICommandWrapper') as ccw, \
                noexit(), stdout() as so:

            @with_defaults
            def main(argument_namespace_callback, **kwargs):
                argument_namespace_callback.output_mode = 'text'
                argument_namespace_callback.text_record_separator = '\0'
                return dict(a='b')
            ccw().main.side_effect = main
            PCLI.main()
        self.assertEqual(so.getvalue(), 'a\tb\0')

    def test_text_list_record_separator(self):
        with patch('PyOpenWorm.cli.CLICommandWrapper') as ccw, \
                noexit(), stdout() as so:

            @with_defaults
            def main(argument_namespace_callback, **kwargs):
                argument_namespace_callback.output_mode = 'text'
                argument_namespace_callback.text_record_separator = '\0'
                return ['a', 'b']
            ccw().main.side_effect = main
            PCLI.main()
        self.assertEqual(so.getvalue(), 'a\0b\0')

    def test_text_uniterable(self):
        target = object()
        with patch('PyOpenWorm.cli.CLICommandWrapper') as ccw, \
                noexit(), stdout() as so:

            @with_defaults
            def main(argument_namespace_callback, **kwargs):
                argument_namespace_callback.output_mode = 'text'
                return target
            ccw().main.side_effect = main
            PCLI.main()
        self.assertEqual(so.getvalue(), str(target) + '\n')

    def test_text_iterable_type_error(self):
        with patch('PyOpenWorm.cli.CLICommandWrapper') as ccw, \
                noexit(), stdout() as so:

            @with_defaults
            def main(argument_namespace_callback, **kwargs):
                argument_namespace_callback.output_mode = 'text'

                def iterable():
                    yield 'blah'
                    yield 'blah'
                    raise TypeError("blah blah")
                return iterable()
            ccw().main.side_effect = main
            with self.assertRaises(TypeError):
                PCLI.main()
            self.assertEqual(so.getvalue(), 'blah\nblah\n')


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
