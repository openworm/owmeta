# -*- coding: utf-8 -*-

from __future__ import absolute_import
import sys
from six.moves import range
sys.path.insert(0, ".")
import rdflib
import rdflib as R
import os


USE_BINARY_DB = False
BINARY_DB = "worm.db"
TEST_CONFIG = "tests/test_default.conf"
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

namespaces = {"rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#"}


def clear_graph(graph):
    graph.update("CLEAR ALL")


def make_graph(size=100):
    """ Make an rdflib graph """
    g = R.Graph()
    for i in range(size):
        s = rdflib.URIRef("http://somehost.com/s" + str(i))
        p = rdflib.URIRef("http://somehost.com/p" + str(i))
        o = rdflib.URIRef("http://somehost.com/o" + str(i))
        g.add((s, p, o))
    return g


def delete_zodb_data_store(path):
    os.unlink(path)
    os.unlink(path + '.index')
    os.unlink(path + '.tmp')
    os.unlink(path + '.lock')


def copy_zodb_data_store(path, new_path):
    import shutil
    shutil.copy2(path, new_path)
    shutil.copy2(path + ".index", new_path + ".index")
    shutil.copy2(path + ".tmp", new_path + ".tmp")
    shutil.copy2(path + ".lock", new_path + ".lock")

