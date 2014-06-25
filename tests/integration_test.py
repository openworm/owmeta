import unittest
from PyOpenWorm import *

TestConfig = Configure.open("tests/test.conf")
Configureable.default = TestConfig

class IntegrationTest(unittest.TestCase):
    """ Integration testing """
    def test_1(self):
        import bibtex
        bt = bibtex.parse("my.bib")
        n1 = Neuron("AVAL")
        n2 = Neuron("DA3")
        c = Connection(pre=n1,post=n2,synclass="synapse")
        e = Evidence(bibtex=bt['white86'])
        e.asserts(c)

    def test_2(self):
        # Reference two neurons
        n1 = Neuron(name='AVAL')
        n2 = Neuron(name='PVCR')

        # Declare a connection between them
        c = Connection(n1,n2,number=1)

        # Attach some evidence for the connection
        e = Evidence(person="Danny Glover")
        e.asserts(c)
        # look at what else this evidence has stated
        r = e.asserts()
        for x in r:
            print "\t".join([str(y)[:60] for y in x])


# XXX: OTHER TESTS TO DO
# reference a synaptic connection
# assert that some source affirms that connection
# look at other sources that affirm the connection
# look at who uploaded these sources and when
#
# look at what else one of these people said
