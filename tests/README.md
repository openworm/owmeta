PyOpenWorm Tests
================

This directory contains the unit and integration tests for PyOpenWorm.

The main test file is test.py.  

test.py itself contains many tests, but also imports tests from additional files
in this directory:

* ConfigureTest.py - Tests for the Configure class, which provides
  functionality to modules to allow outside objects to parameterize their
  behavior
* DataIntegrityTest.py - Integration tests that read from the database and
  ensure that basic queries have expected answers, as a way to keep data quality
  high.
* DatabaseBackendTest.py - Integration tests that ensure basic functioning of
  the database backend and connection
* ExampleRunnerTest.py
* integration_test.py
* PintTest.py
* QuantityTest.py
* RDFLibTest.py
* test_data.py
