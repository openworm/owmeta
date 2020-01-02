import unittest
from owmeta.datasource_loader import DataSourceDirLoader, LoadFailed
from os.path import realpath, relpath, join
from os import getcwd, makedirs, unlink
from tempfile import TemporaryDirectory


class DataSourceDirLoaderTest(unittest.TestCase):
    def test_dirname(self):
        with TemporaryDirectory() as d:
            reldir = relpath(d, getcwd())
            cut = DataSourceDirLoader(reldir)
            self.assertEqual(d, cut.base_directory)

    def test_load_no_ident(self):
        class A(DataSourceDirLoader):
            def load(self, ident):
                pass
        cut = A('dir')
        with self.assertRaises(LoadFailed):
            cut('ident')

    def test_load_empty_ident(self):
        class A(DataSourceDirLoader):
            def load(self, ident):
                return ''
        cut = A('dir')
        with self.assertRaises(LoadFailed):
            cut('ident')

    def test_load_returns_non_dir(self):
        with TemporaryDirectory() as e, TemporaryDirectory() as d:
            dname = join(d, 'dir')
            makedirs(dname)

            sm = join(e, 'nom')
            makedirs(sm)

            class A(DataSourceDirLoader):
                def load(self, ident):
                    return sm

            cut = A(dname)

            with self.assertRaisesRegexp(LoadFailed, r'outside of the base'):
                cut('ident')

    def test_load_success(self):
        class A(DataSourceDirLoader):
            def load(self, ident):
                return 'nom'
        with TemporaryDirectory() as d:
            dname = join(d, 'dir')
            sm = join(dname, 'nom')
            makedirs(sm)
            cut = A(dname)
            cut('ident')
