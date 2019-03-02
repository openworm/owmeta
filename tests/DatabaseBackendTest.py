# -*- coding: utf-8 -*-

from __future__ import absolute_import
import unittest
from PyOpenWorm.configure import Configure, Configureable
from PyOpenWorm.data import Data
from PyOpenWorm import connect, config, disconnect
import rdflib as R
import os
import subprocess
import tempfile
import traceback

from .GraphDBInit import delete_zodb_data_store, make_graph, has_bsddb


class DatabaseBackendTest(unittest.TestCase):
    ''' Integration tests for the database backend '''
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
        """ Should be able to init without these values """
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

    @unittest.skipIf((has_bsddb is False), "Sleepycat requires working bsddb")
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
