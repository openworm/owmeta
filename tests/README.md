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
* ExampleRunnerTest.py - Runs the examples to make sure we didn't break the API
  for them.
* QuantityTest.py - Tests our Quantity class, which is used for defining things
  with measurement units
* RDFLibTest.py

* integration_test.py - Apparently orphaned test class.  TODO: Integrate this guy
* test_data.py
