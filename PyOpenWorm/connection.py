"""
.. class:: Connection

   connection
   =============

   Connection between neurons

"""
import PyOpenWorm as P
from PyOpenWorm import *
from string import Template
import rdflib as R

__all__ = ['Connection']

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

        DatatypeProperty('syntype',owner=self)
        DatatypeProperty('synclass',owner=self)
        DatatypeProperty('number',owner=self)
        ObjectProperty('pre_cell',owner=self)
        ObjectProperty('post_cell',owner=self)

        if isinstance(pre_cell,P.Neuron):
            self.pre_cell(pre_cell)
        elif pre_cell is not None:
            self.pre_cell(P.Neuron(name=pre_cell, conf=self.conf))

        if (isinstance(post_cell,P.Neuron)):
            self.post_cell(post_cell)
        elif post_cell is not None:
            self.post_cell(P.Neuron(name=post_cell, conf=self.conf))

        if isinstance(number,int):
            self.number(int(number))
        elif number is not None:
            raise Exception("Connection number must be an int, given %s" % number)

        if isinstance(syntype,basestring):
            syntype=syntype.lower()
            if syntype in ('send', SynapseType.Chemical):
                self.syntype(SynapseType.Chemical)
            elif syntype in ('gapjunction', SynapseType.GapJunction):
                self.syntype(SynapseType.GapJunction)
        if isinstance(synclass,basestring):
            self.synclass(synclass)

    def __str__(self):
        return "Connection from %s to %s (%s times, type: %s, neurotransmitter: %s)"%(self.pre_cell, self.post_cell, self.number, self.syntype, self.synclass)

def _dict_to_sparql_binds(d):
    return "\n".join('filter(' + d[x] + ' = ?' + x + ')' for x in d)
