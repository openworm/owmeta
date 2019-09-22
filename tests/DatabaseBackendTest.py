# -*- coding: utf-8 -*-

from __future__ import absolute_import
import unittest
from owmeta.configure import Configure, Configureable
from owmeta.data import Data
from owmeta import connect, config, disconnect
import rdflib as R
import os
import subprocess
import tempfile
import traceback
import shutil

from .GraphDBInit import delete_zodb_data_store, make_graph, has_bsddb


class DatabaseBackendTest(unittest.TestCase):
    ''' Integration tests for the database backend '''

    def setUp(self):
        self.testdir = tempfile.mkdtemp(prefix=__name__ + '.')
        self.startdir = os.getcwd()
        os.chdir(self.testdir)

    def tearDown(self):
        os.chdir(self.startdir)
        shutil.rmtree(self.testdir)

    def test_namespace_manager(self):
        c = Configure()
        c['rdf.source'] = 'default'
        c['rdf.store'] = 'default'
        Configureable.default = c
        d = Data()
        d.openDatabase()

        self.assertIsInstance(d['rdf.namespace_manager'], R.namespace.NamespaceManager)

    def test_init_no_rdf_store(self):
        """ Should be able to init without these values """
        c = Configure()
        Configureable.default = c
        d = Data()
        try:
            d.openDatabase()
        except Exception:
            self.fail("Bad state")

    def test_ZODB_persistence(self):
        c = Configure()
        fname = 'ZODB.fs'
        c['rdf.source'] = 'ZODB'
        c['rdf.store_conf'] = fname
        Configureable.default = c
        d = Data()
        try:
            d.openDatabase()
            g = make_graph(20)
            for x in g:
                d['rdf.graph'].add(x)
            d.closeDatabase()

            d.openDatabase()
            self.assertEqual(20, len(list(d['rdf.graph'])))
            d.closeDatabase()
        except Exception:
            traceback.print_exc()
            self.fail("Bad state")
        delete_zodb_data_store(fname)

    def test_sqlite3_persistence(self):
        c = Configure()
        fname = 'sqlite.db'
        c['rdf.source'] = 'sqlite'
        c['rdf.store_conf'] = fname
        Configureable.default = c
        d = Data()
        try:
            d.openDatabase()
            g = make_graph(20)
            for x in g:
                d['rdf.graph'].add(x)
            d.closeDatabase()

            d.openDatabase()
            self.assertEqual(20, len(list(d['rdf.graph'])))
            d.closeDatabase()
        except Exception:
            traceback.print_exc()
            self.fail("Bad state")
        os.unlink(fname)

    @unittest.skipIf(not has_bsddb, "Sleepycat requires working bsddb")
    def test_Sleepycat_persistence(self):
        """ Should be able to init without these values """
        c = Configure()
        fname = 'Sleepycat_store'
        c['rdf.source'] = 'Sleepycat'
        c['rdf.store_conf'] = fname
        Configureable.default = c
        d = Data()
        try:
            d.openDatabase()
            g = make_graph(20)
            for x in g:
                d['rdf.graph'].add(x)
            d.closeDatabase()

            d.openDatabase()
            self.assertEqual(20, len(list(d['rdf.graph'])))
            d.closeDatabase()
        except Exception:
            traceback.print_exc()
            self.fail("Bad state")

        subprocess.call("rm -rf "+fname, shell=True)
