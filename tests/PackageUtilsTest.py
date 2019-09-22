from __future__ import absolute_import
from owmeta.collections import Bag
from owmeta.package_utils import get_library_location
import unittest
from os.path import join, dirname


class PackageUtilsTest(unittest.TestCase):
    def test_package_path(self):
        self.assertEquals(join(dirname(__file__), 'tmod'),
                          get_library_location('tests.tmod'))
