from __future__ import absolute_import
from __future__ import print_function
import owmeta_core
import unittest
import subprocess
import tempfile

from owmeta_core.context import Context
from owmeta_core.data import Data
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

    def setUp(self):
        self.TestConfig = Data.open(TEST_CONFIG)
        td = '__tempdir__'
        z = self.TestConfig['rdf.store_conf']
        if z.startswith(td):
            x = z[len(td):]
            h = tempfile.mkdtemp()
            self.TestConfig['rdf.store_conf'] = h + x
        self.delete_dir()
        self.connection = owmeta_core.connect(conf=self.TestConfig)
        self.context = Context(ident='http://example.org/test-context',
                               conf=self.TestConfig)
        typ = type(self)
        if hasattr(typ, 'ctx_classes'):
            if isinstance(dict, typ.ctx_classes):
                self.ctx = self.context(typ.ctx_classes)
            else:
                self.ctx = self.context({x.__name__: x for x in typ.ctx_classes})

    def save(self):
        self.context.save_context()

    def tearDown(self):
        owmeta_core.disconnect(self.connection)
        self.delete_dir()

    @property
    def config(self):
        return self.TestConfig
    conf = config
