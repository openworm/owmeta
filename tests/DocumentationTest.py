# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
import unittest
import doctest
import os
from os.path import join as p
import tempfile
import shutil
from .doctest_plugin import ALLOW_UNICODE, UnicodeOutputChecker
from .TestUtilities import xfail_without_db


doctest.OutputChecker = UnicodeOutputChecker


class DocumentationTest(unittest.TestCase):
    ''' Executes doctests '''
    def setUp(self):
        xfail_without_db()
        self.startdir = os.getcwd()
        self.testdir = tempfile.mkdtemp(prefix=__name__ + '.')
        shutil.copytree('.pow', p(self.testdir, '.pow'), symlinks=True)
        shutil.copyfile('README.md', p(self.testdir, 'README.md'))
        shutil.copyfile('readme.conf', p(self.testdir, 'readme.conf'))
        os.chdir(self.testdir)

    def tearDown(self):
        os.chdir(self.startdir)

    def test_readme(self):
        [failure_count, return_count] = doctest.testfile("README.md", module_relative=False,
                                                         optionflags=(ALLOW_UNICODE | doctest.ELLIPSIS))
        self.assertEqual(failure_count, 0)
