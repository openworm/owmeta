import unittest
import traceback
import rdflib as R
from PyOpenWorm import *

class IntegrationTest(unittest.TestCase):
    """ Integration testing """
    def setUp(self):
        connect("tests/test.conf")

    def tearDown(self):
        disconnect()

    @unittest.skip("No bibtex module")
    def test_1(self):
        import bibtex
        bt = bibtex.parse("my.bib")
        n1 = Neuron("AVAL")
        n2 = Neuron("DA3")
        c = Connection(pre_cell=n1,post_cell=n2,synclass="synapse")
        e = Evidence(bibtex=bt['white86'])
        e.asserts(c)
        print list(e.load())

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
        print e.conf
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
    def test_evidence_asserts_all_about(self):
        """ Test that we can assert_all_about a containing object and
        then get evidence for contained objects.
        """
        import random
        random.seed()
        v = values('all')
        def make_syn():
            import struct
            u = struct.pack("=2f",random.random(),random.random())
            z = struct.pack("=2f",random.random(),random.random())
            a = Neuron(u.encode('hex'))
            b = Neuron(z.encode('hex'))
            v.value(a.neighbor(b))
            return (a,b)

        for x in range(200):
            make_syn()

        # the one we'll check for
        a,b = make_syn()
        ev = Evidence(author="Homer")
        ev.asserts_all_about(ev)
        ev.save()
        eve = Evidence()
        eve.asserts(a.neighbor(b))
        for x in eve.load():
            print x

    def testl(self):
        """
        Test that a property can be loaded when the owning
        object doesn't have any other values set
        This test is for many objects of the same kind
        """
        from random import random
        from time import time
        from subprocess import call
        import os
        # Generate data sets from 10 to 10000 in size
        #  query for properties
        print 'starting testl'
        class _to(DataObject):
            def __init__(self,x=False):
                DataObject.__init__(self)
                DatatypeProperty('flexo',owner=self)
                if x:
                    self.flexo(x)
        # feel free to add more if you have the time
        nums = [10, 1e2, 1e3]

        Configureable.default = Data.open("tests/test_testl.conf")
        Configureable.default.openDatabase()
        try:
            #for 1000, takes about 10 seconds...
            for x in nums:
                print 'running ',x,'sized test on a ',Configureable.default['rdf.graph'].store,'store'
                v = values('zim')
                for z in range(int(x)):
                    v.add(_to(random()))
                t0 = time()
                v.save()
                for _ in _to().flexo():
                    pass
                t1 = time()
                print "took", t1 - t0, "seconds"
                Configureable.default['rdf.graph'].remove((None,None,None))
        except:
            traceback.print_exc()
        Configureable.default.closeDatabase()

# XXX: OTHER TESTS TO DO
# reference a synaptic connection
# assert that some source affirms that connection
# look at other sources that affirm the connection
# look at who uploaded these sources and when
#
# look at what else one of these people said
