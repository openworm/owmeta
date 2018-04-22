from __future__ import absolute_import
from __future__ import print_function
import PyOpenWorm
import unittest
import subprocess
import tempfile

from PyOpenWorm.context import Context
from PyOpenWorm.configure import Configure
from .GraphDBInit import delete_zodb_data_store, TEST_CONFIG


class _DataTest(unittest.TestCase):

    def delete_dir(self):
        self.path = self.TestConfig['rdf.store_conf']
        try:
            if self.TestConfig['rdf.source'] == "Sleepycat":
                subprocess.call("rm -rf " + self.path, shell=True)
            elif self.TestConfig['rdf.source'] == "ZODB":
                delete_zodb_data_store(self.path)
        except OSError as e:
            if e.errno == 2:
                # The file may not exist and that's fine
                pass
            else:
                raise e

    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        # Set do_logging to True if you like walls of text
        self.TestConfig = Configure.open(TEST_CONFIG)
        td = '__tempdir__'
        z = self.TestConfig['rdf.store_conf']
        if z.startswith(td):
            x = z[len(td):]
            h = tempfile.mkdtemp()
            self.TestConfig['rdf.store_conf'] = h + x
        self.delete_dir()
        PyOpenWorm.connect(conf=self.TestConfig, do_logging=False)
        self.context = Context(ident='http://example.org/test-context')
        typ = type(self)
        if hasattr(typ, 'ctx_classes'):
            if isinstance(dict, typ.ctx_classes):
                self.ctx = self.context(typ.ctx_classes)
            else:
                self.ctx = self.context({x.__name__: x for x in typ.ctx_classes})
        self.save = lambda: self.context.save_context(PyOpenWorm.config('rdf.graph'))

    def tearDown(self):
        PyOpenWorm.disconnect()
        self.delete_dir()

    @property
    def config(self):
        return PyOpenWorm.config()
