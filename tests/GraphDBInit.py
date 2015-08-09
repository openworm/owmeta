# -*- coding: utf-8 -*-

import sys
sys.path.insert(0,".")
import unittest
import neuroml
import neuroml.writers as writers
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

USE_BINARY_DB = False
BINARY_DB = "OpenWormData/worm.db"
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
