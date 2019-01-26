import unittest

try:
    from unittest.mock import patch, Mock
except ImportError:
    from mock import patch, Mock

from pytest import mark
from PyOpenWorm.command_util import SubCommand, IVar
from PyOpenWorm.cli_command_wrapper import CLICommandWrapper
import PyOpenWorm.cli as PCLI
from six import StringIO
from contextlib import contextmanager


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


@mark.inttest
class CLITest(unittest.TestCase):
    def test_cli(self):
        with patch('sys.argv', ['command']), noexit(), stderr() as se:
            PCLI.main()
        self.assertIn('usage: command', se.getvalue())


@contextmanager
def noexit():
    try:
        yield
    except SystemExit:
        pass


@contextmanager
def stdout():
    import sys
    oldstdout = sys.stdout
    sio = StringIO()
    sys.stdout = sio
    try:
        yield sys.stdout
    finally:
        sys.stdout = oldstdout


@contextmanager
def stderr():
    import sys
    oldstderr = sys.stderr
    sio = StringIO()
    sys.stderr = sio
    try:
        yield sys.stderr
    finally:
        sys.stderr = oldstderr
