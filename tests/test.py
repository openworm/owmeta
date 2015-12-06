from __future__ import print_function
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
import logging
import pint as Q
import os
import subprocess as SP
import subprocess
import tempfile
import doctest

from glob import glob

# Import configuration files for tests and create worm graph
# TODO: Please update this description!
from GraphDBInit import *

# Tests for the Configure class, which provides functionality to modules to
# allow outside objects to parameterize their behavior
from ConfigureTest import ConfigureTest

# Integration tests that read from the database and ensure that basic queries
# have expected answers, as a way to keep data quality high.
from DataIntegrityTest import DataIntegrityTest

# Integration tests that ensure basic functioning of the database backend and
# connection
from DatabaseBackendTest import DatabaseBackendTest

# Runs the examples to make sure we didn't break the API for them.
from ExampleRunnerTest import ExampleRunnerTest

# Tests our Quantity class, which is used for defining things with measurement
# units
from QuantityTest import QuantityTest

# Tests RDFLib, our backend library that interfaces with the database as an
# RDF graph.
from RDFLibTest import RDFLibTest

# Import _DataTest
# TODO: Add description for this set of tests
from DataTestTemplate import _DataTest

# Test for Worm
# TODO: Add description for this set of tests
from WormTest import WormTest

# CellTest
# Test various properties of Cell objects. For example, that we can get
# the parent of a cell, or the children, etc.
from CellTest import CellTest

# DataObjectTest
# TODO: Add description for this set of tests
from DataObjectTest import DataObjectTest

# DataUserTest
# Test basic operations on DataObjects
from DataUserTest import DataUserTest

# ChannelTest
# Test basic operations on Channel objects.
from ChannelTest import ChannelTest

# ExperimentTest
# Test basic operations on Experiment objects.
from ExperimentTest import ExperimentTest

# NeuronTest
# Test basic operations on Neuron objects. For example, that that two Neuron
# objects with the same name have the same identifier.
from NeuronTest import NeuronTest

# NetworkTest
# Basic tests for neuron network
from NetworkTest import NetworkTest

# EvidenceTest
# Tests for the Evidence object capabilities/functions
from EvidenceTest import EvidenceTest

# EvidenceCoverageTest
# Tests for evidence for objects in the PyOpenWorm database
from EvidenceCoverageTest import EvidenceCoverageTest

# ConnectionTest
# TODO: Add description for this set of tests
from ConnectionTest import ConnectionTest

# Muscle Test
# Tests for various properties of Muscle objects.
from MuscleTest import MuscleTest

# PlotTest
# Tests for the Plot data object
from PlotTest import PlotTest

# Property Test
# TODO: Add description for this set of tests
from PropertyTest import PropertyTest

# SimplePropertyTest
# Sanity checks for DataObjects.  For example, that two objects with the same
# name have the same identifier.
from SimplePropertyTest import SimplePropertyTest

# NeuroMLTest
# TODO: Add description for this set of tests
# TODO: This test is empty!
from NeuroMLTest import NeuroMLTest

# InferenceTest
from InferenceTest import InferenceTest

# Miscellaneous Tests
# These are tests for miscellaneous bugs that have come up.
from MiscTest import MiscTest

# Tests from README.md
from DocumentationTest import DocumentationTest

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-b", "--use-binary-database", dest="binary_db",
                      action="store_true", default=False,
                      help="Use the binary database for data integrity tests")
    parser.add_option("-l", "--do-logging", dest="do_logging",
                      action="store_true", default=False,
                      help="Turn on log output")

    (options, args) = parser.parse_args()
    USE_BINARY_DB = options.binary_db

    if options.do_logging:
        logging.basicConfig(level=logging.DEBUG, format="%(levelname)s:%(name)s:%(lineno)s:%(message)s")

    def getTests(testCase):
        test_loader = unittest.TestLoader()
        return test_loader.loadTestsFromTestCase(testCase)

    def runTests(suite):
        return unittest.TextTestRunner().run(suite)

    all_tests = []
    configs = glob("tests/test_*.conf")
    if not has_bsddb:
        configs = [x for x in configs if 'Sleepycat' not in x]
    print("Testing with configs:",configs)
    for x in configs:
        TEST_CONFIG = x
        suite = unittest.TestSuite()
        suite.addTests(getTests(x) for x in _DataTest.__subclasses__())
        all_tests.append(suite)

    suite = unittest.TestSuite()
    classes = filter(lambda x : isinstance(x, type), globals().values())
    non_DataTestTests = (x for x in classes if (issubclass(x, unittest.TestCase) and not issubclass(x,  _DataTest)))
    suite.addTests(getTests(x) for x in non_DataTestTests)
    all_tests.append(suite)

    all_tests_flattened = []
    for x in all_tests:
        for y in x:
            for z in y:
                all_tests_flattened.append(z)

    suite = unittest.TestSuite()

    if len(args) == 1:
        suite.addTests(filter(lambda x: x.id().startswith(args[0]), all_tests_flattened))
    else:
        suite.addTests(all_tests)

    res = runTests(suite)
    sys.exit(len(res.failures + res.errors)>0)
