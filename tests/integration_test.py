import unittest
import rdflib as R
from PyOpenWorm import *

TestConfig = Data.open("tests/test.conf")
Configureable.default = TestConfig

class IntegrationTest(unittest.TestCase):
    """ Integration testing """
    def setUp(self):
        self.config = TestConfig
        self.config.openDatabase()

    def tearDown(self):
        self.config.closeDatabase()

    def test_1(self):
        import bibtex
        bt = bibtex.parse("my.bib")
        n1 = Neuron("AVAL")
        n2 = Neuron("DA3")
        c = Connection(pre_cell=n1,post_cell=n2,synclass="synapse")
        e = Evidence(bibtex=bt['white86'])
        e.asserts(c)

    def test_2(self):
        # Reference two neurons
        n1 = Neuron(name='AVAL')
        n2 = Neuron(name='PVCR')

        # Declare a connection between them
        c = Connection(n1,n2,number=1)

        # Attach some evidence for the connection
        e = Evidence(author="Danny Glover")
        e.asserts(c)
        # look at what else this evidence has stated
        e.save()
        e = Evidence(author="Danny Glover")
        r = e.asserts()
        for x in r:
            print x
            #print "\t".join([str(y)[:60] for y in x])
    def test_get_evidence(self):
        # Reference two neurons
        n1 = Neuron(name='AVAL')
        n2 = Neuron(name='PVCR')

        # Declare a connection between them
        c = Connection(n1,n2,number=1)
        e = Evidence()
        # Create an Evidence search-object
        e.asserts(c)

        # look for all of the evidence for the connection 'c'
        for x in e.load():
            print x.author()
    def test_get_synclasses(self):
        c = Connection()
        for x in c.synclass():
            print x

# XXX: OTHER TESTS TO DO
# reference a synaptic connection
# assert that some source affirms that connection
# look at other sources that affirm the connection
# look at who uploaded these sources and when
#
# look at what else one of these people said
