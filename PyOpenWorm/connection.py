"""
.. class:: Connection

   connection
   =============

   Connection between neurons

"""
import PyOpenWorm as P
from PyOpenWorm import Relationship,Neuron,SimpleProperty
from string import Template
import rdflib as R

class SynapseType:
    Chemical = "send"
    GapJunction = "gapJunction"
class Connection(Relationship):
    def __init__(self,
                 pre_cell=None,
                 post_cell=None,
                 number=None,
                 syntype=None,
                 synclass=None,
                 **kwargs):
        Relationship.__init__(self,**kwargs)

        self.syntype = SimpleProperty(self,'syntype')
        self.synclass = SimpleProperty(self,'neurotransmitter')
        self.number = SimpleProperty(self,'number')
        self.pre_cell = SimpleProperty(self,'pre')
        self.post_cell = SimpleProperty(self,'post')

        if isinstance(pre_cell,Neuron):
            self.pre_cell(pre_cell)
        elif pre_cell is not None:
            self.pre_cell(Neuron(name=pre_cell, conf=self.conf))

        if (isinstance(post_cell,Neuron)):
            self.post_cell(post_cell)
        elif post_cell is not None:
            self.post_cell(Neuron(name=post_cell, conf=self.conf))

        if isinstance(number,int):
            self.number(int(number))

        if isinstance(syntype,basestring):
            syntype=syntype.lower()
            if syntype in ('send', SynapseType.Chemical):
                self.syntype(SynapseType.Chemical)
            elif syntype in ('gapjunction', SynapseType.GapJunction):
                self.syntype(SynapseType.GapJunction)
        if isinstance(synclass,basestring):
            self.synclass(synclass)

    def load(self):
        qres = P.DataObject.load(self)
        for r in qres:
            try:
                yield Connection(pre_cell=Neuron(ident=r['pre']), post_cell=Neuron(ident=r['post']), syntype=r['syntype'], number=r['number'])
            except BaseException, e:
                print e

    def __str__(self):
        return "Connection from %s to %s (%s times, type: %s, neurotransmitter: %s)"%(self.pre_cell, self.post_cell, self.number, self.syntype, self.synclass)

def _dict_to_sparql_binds(d):
    return "\n".join('filter(' + d[x] + ' = ?' + x + ')' for x in d)
