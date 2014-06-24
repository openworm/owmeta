"""
.. class:: Connection

   connection
   =============

   Connection between neurons

"""
from PyOpenWorm import Relationship,Neuron
import rdflib as R

class Connection(Relationship):
    def __init__(self,
                 pre_cell,
                 post_cell,
                 number,
                 syntype=None,
                 synclass=None,
                 conf=False):
        Relationship.__init__(self,conf=conf)
        self.namespace = R.Namespace(self.conf['rdf.namespace']['Connection'] + '/')
        if isinstance(pre_cell,Neuron):
            assert(isinstance(post_cell,Neuron))
            self.pre_cell = pre_cell
            self.post_cell = post_cell
        else:
            self.pre_cell = Neuron(name=pre_cell, conf=self.conf)
            self.post_cell = Neuron(name=post_cell, conf=self.conf)
        self.number = int(number)
        self.syntype = syntype
        self.synclass = synclass

    def identifier(self):
        data = (self.pre_cell, self.post_cell, self.number,self.syntype, self.synclass)
        print data
        return self.conf['molecule_name'](data)

    def triples(self):
        pre_cell = self.pre_cell.identifier()
        post_cell = self.post_cell.identifier()
        yield (pre_cell, self.conf['rdf.namespace']['356'], post_cell)
        ident = self.identifier()
        yield (ident, self.namespace['pre'], pre_cell)
        yield (ident, self.namespace['syntype'], self.conf['rdf.namespace']['356'])
        yield (ident, self.namespace['post'], post_cell)

    def __str__(self):
        return "Connection from %s to %s (%i times, type: %s, neurotransmitter: %s)"%(self.pre_cell, self.post_cell, self.number, self.syntype, self.synclass)
