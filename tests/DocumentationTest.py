# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
import unittest
import doctest
import os
from os.path import join as p
import tempfile
import shutil
from collections import namedtuple
import importlib as IM

import pytest

from .doctest_plugin import ALLOW_UNICODE, UnicodeOutputChecker
from .TestUtilities import xfail_without_db


doctest.OutputChecker = UnicodeOutputChecker


@pytest.mark.inttest
class READMETest(unittest.TestCase):
    ''' Executes doctests '''
    def setUp(self):
        xfail_without_db()
        self.startdir = os.getcwd()
        self.testdir = tempfile.mkdtemp(prefix=__name__ + '.')
        shutil.copytree('.owm', p(self.testdir, '.owm'), symlinks=True)
        shutil.copyfile('README.md', p(self.testdir, 'README.md'))
        shutil.copyfile('readme.conf', p(self.testdir, 'readme.conf'))
        os.chdir(self.testdir)

    def tearDown(self):
        os.chdir(self.startdir)
        shutil.rmtree(self.testdir)

    def test_readme(self):
        [failure_count, return_count] = doctest.testfile("README.md", module_relative=False,
                                                         optionflags=(ALLOW_UNICODE | doctest.ELLIPSIS))
        self.assertEqual(failure_count, 0)


class SphinxTest(unittest.TestCase):
    ''' Executes doctests in Sphinx documentation '''
    def setUp(self):
        self.startdir = os.getcwd()
        self.testdir = tempfile.mkdtemp(prefix=__name__ + '.')
        shutil.copytree('docs', p(self.testdir, 'docs'))
        os.chdir(self.testdir)

    def tearDown(self):
        os.chdir(self.startdir)
        shutil.rmtree(self.testdir)

    def execute(self, fname, **kwargs):
        failure_count, _ = doctest.testfile(p('docs', fname + '.rst'), module_relative=False,
                optionflags=(ALLOW_UNICODE | doctest.ELLIPSIS), **kwargs)
        self.assertEqual(failure_count, 0)

    def test_adding_data(self):
        # Setup a class imported by docs for demonstration purposes
        from owmeta_core.dataobject import DataObject, DatatypeProperty
        from owmeta_core.context import Context
        Load = lambda *args, **kwargs: [namedtuple('Record', ('pnum', 'flns', 'hrds'))(12, 1.0, 100)]

        class Widget(DataObject):
            class_context = 'http://example.org/test_adding_data'
            rdf_type = 'http://example.org/BDW/schema/Widget'
            rdf_namespace = 'http://example.org/BDW/entities/Widget#'
            hardiness = DatatypeProperty()
            fullness = DatatypeProperty()
            part_number = DatatypeProperty()
            key_property = {'name': 'part_number', 'type': 'direct'}

        ctx = Context(ident='http://example.org/data/imports/BDW_Widgets_2018-2019')

        ctx.mapper.process_class(Widget)
        ctx(Widget)(part_number=15)
        ctx(Widget)(part_number=17)
        ctx(Widget)(part_number=20)

        self.execute('adding_data', extraglobs={'Load': Load, 'Widget': Widget, 'ctx18': ctx})


def doctest_mod(module_name):
    mod = IM.import_module(module_name)
    [failure_count, return_count] = doctest.testmod(mod,
            optionflags=ALLOW_UNICODE | doctest.ELLIPSIS)
    assert failure_count == 0


def test_channelworm():
    doctest_mod('owmeta.channelworm')


def test_neuroml():
    doctest_mod('owmeta.neuroml')


def test_cell():
    doctest_mod('owmeta.cell')
