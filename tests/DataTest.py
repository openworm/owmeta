# -*- coding: utf-8 -*-

import sys
sys.path.insert(0,".")
import unittest
import neuroml
import neuroml.writers as writers
import PyOpenWorm
from PyOpenWorm import *
import test_data as TD
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

USE_BINARY_DB = False
BINARY_DB = "OpenWormData/worm.db"
TEST_CONFIG = "tests/default_test.conf"
try:
    import bsddb
    has_bsddb = True
except ImportError:
    has_bsddb = False

try:
    import numpy
    has_numpy = True
except ImportError:
    has_numpy = False

namespaces = { "rdf" : "http://www.w3.org/1999/02/22-rdf-syntax-ns#" }

def clear_graph(graph):
    graph.update("CLEAR ALL")

def make_graph(size=100):
    """ Make an rdflib graph """
    g = R.Graph()
    for i in range(size):
        s = rdflib.URIRef("http://somehost.com/s"+str(i))
        p = rdflib.URIRef("http://somehost.com/p"+str(i))
        o = rdflib.URIRef("http://somehost.com/o"+str(i))
        g.add((s,p,o))
    return g

def delete_zodb_data_store(path):
    os.unlink(path)
    os.unlink(path + '.index')
    os.unlink(path + '.tmp')
    os.unlink(path + '.lock')

class DataTest(unittest.TestCase):
    def test_namespace_manager(self):
        c = Configure()
        c['rdf.source'] = 'default'
        c['rdf.store'] = 'default'
        Configureable.conf = c
        d = Data()
        d.openDatabase()

        self.assertIsInstance(d['rdf.namespace_manager'], R.namespace.NamespaceManager)

    def test_init_no_rdf_store(self):
        """ Should be able to init without these values """
        c = Configure()
        Configureable.conf = c
        d = Data()
        try:
            d.openDatabase()
        except:
            self.fail("Bad state")

    def test_ZODB_persistence(self):
        """ Should be able to init without these values """
        c = Configure()
        fname ='ZODB.fs'
        c['rdf.source'] = 'ZODB'
        c['rdf.store_conf'] = fname
        Configureable.conf = c
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
        except:
            traceback.print_exc()
            self.fail("Bad state")
        delete_zodb_data_store(fname)

    @unittest.skipIf((has_bsddb==False), "Sleepycat requires working bsddb")
    def test_Sleepycat_persistence(self):
        """ Should be able to init without these values """
        c = Configure()
        fname='Sleepycat_store'
        c['rdf.source'] = 'Sleepycat'
        c['rdf.store_conf'] = fname
        Configureable.conf = c
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
        except:
            traceback.print_exc()
            self.fail("Bad state")

        subprocess.call("rm -rf "+fname, shell=True)

    def test_trix_source(self):
        """ Test that we can load the datbase up from an XML file.
        """
        f = tempfile.mkstemp()

        c = Configure()
        c['rdf.source'] = 'trix'
        c['rdf.store'] = 'default'
        c['trix_location'] = f[1]

        with open(f[1],'w') as fo:
            fo.write(TD.TriX_data)

        connect(conf=c)
        c = config()

        try:
            g = c['rdf.graph']
            b = g.query("ASK { ?S ?P ?O }")
            for x in b:
                self.assertTrue(x)
        except ImportError:
            pass
        finally:
            disconnect()
        os.unlink(f[1])

    def test_trig_source(self):
        """ Test that we can load the datbase up from a trig file.
        """
        f = tempfile.mkstemp()

        c = Configure()
        c['rdf.source'] = 'serialization'
        c['rdf.serialization'] = f[1]
        c['rdf.serialization_format'] = 'trig'
        c['rdf.store'] = 'default'
        with open(f[1],'w') as fo:
            fo.write(TD.Trig_data)

        connect(conf=c)
        c = config()

        try:
            g = c['rdf.graph']
            b = g.query("ASK { ?S ?P ?O }")
            for x in b:
                self.assertTrue(x)
        except ImportError:
            pass
        finally:
            disconnect()
