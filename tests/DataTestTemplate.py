import sys
sys.path.insert(0,".")
import unittest

import PyOpenWorm
from PyOpenWorm import *
import networkx
import rdflib
import rdflib as R
import pint as Q
import os
import subprocess as SP
import subprocess
import tempfile
import doctest

from glob import glob

from GraphDBInit import *

class _DataTest(unittest.TestCase):
    def delete_dir(self):
        self.path = self.TestConfig['rdf.store_conf']
        try:
            if self.TestConfig['rdf.source'] == "Sleepycat":
                subprocess.call("rm -rf "+self.path, shell=True)
            elif self.TestConfig['rdf.source'] == "ZODB":
                delete_zodb_data_store(self.path)
        except OSError, e:
            if e.errno == 2:
                # The file may not exist and that's fine
                pass
            else:
                raise e
    def setUp(self):
        # Set do_logging to True if you like walls of text
        self.TestConfig = Configure.open(TEST_CONFIG)
        td = '__tempdir__'
        z = self.TestConfig['rdf.store_conf']
        if z.startswith(td):
            x = z[len(td):]
            h=tempfile.mkdtemp()
            self.TestConfig['rdf.store_conf'] = h + x
        self.delete_dir()
        PyOpenWorm.connect(conf=self.TestConfig, do_logging=False)

    def tearDown(self):
        PyOpenWorm.disconnect()
        self.delete_dir()

    @property
    def config(self):
        return PyOpenWorm.config()
