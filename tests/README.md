owmeta Tests
============

Run tests by executing the following from your command line.

    $ py.test

To run only tests which integrate with components outside of owmeta's control (e.g., web services) run this command:

    $ py.test -m 'inttest'

or, to exclude such tests:

    $ py.test -m 'not inttest'

This directory contains the unit and integration tests for owmeta.

* ConfigureTest.py - Tests for the Configuration class, which provides
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
* RDFLibTest.py - Tests RDFLib, our backend library that interfaces with the
  database as an RDF graph.

In addition, there are other files in this directory:

* integration_test.py - Apparently orphaned test class.  TODO: Integrate this guy

The .conf files in this directory are used to put different configuration
parameters into different tests.  

* test_default.conf
* test_ZODB.conf
* testl.conf

Some key configuration variables that can be used include:

To change to a sparql_endpoint backend:

rdf.source = "sparql_endpoint"
rdf.store_conf = ["http://107.170.133.175:8080/openrdf-sesame/repositories/test","http://107.170.133.175:8080/openrdf-sesame/repositories/test/statements"]

To change to a sleepycat backend:

"rdf.store" : "Sleepycat",
"rdf.store_conf" : "testl.db",
"rdf.upload_block_statement_count" : 50,

* test_data.py -- this is a python file that is acting as test data.

Test data is located in the test_data directory:

* test_data/PVDR.nml.rdf.xml - Sample data in TriG format to demonstrate we can
  parse it.
* test_data/bad_test.conf - Sample .conf file for a test that ensures corrupt
  configuration files will not load (in ConfigureTest)
