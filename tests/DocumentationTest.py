# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
import unittest
import doctest
from .doctest_plugin import ALLOW_UNICODE, UnicodeOutputChecker


doctest.OutputChecker = UnicodeOutputChecker


class DocumentationTest(unittest.TestCase):
    ''' Executes doctests '''
    def test_readme(self):
        [failure_count, return_count] = doctest.testfile("../README.md", optionflags=(ALLOW_UNICODE | doctest.ELLIPSIS))
        self.assertEqual(failure_count, 0)
