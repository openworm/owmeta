"""
.. class:: Connection

   connection
   =============

   Connection between neurons

"""
from PyOpenWorm import Relationship,Neuron

class Connection(Relationship):
    def __init__(self,
                 pre_cell,
                 post_cell,
                 number=None,
                 syntype=None,
                 synclass=None,
                 conf=False):
        Relationship.__init__(self,conf=conf)
        if isinstance(pre_cell,Neuron):
            assert(isinstance(post_cell,Neuron))
        else:
            self.pre_cell = Neuron(name=pre_cell, conf=self.conf)
            self.post_cell = Neuron(name=post_cell, conf=self.conf)
            self.number = int(number)
            self.syntype = syntype
            self.synclass = synclass


    def __str__(self):
        return "Connection from %s to %s (%i times, type: %s, neurotransmitter: %s)"%(self.pre_cell, self.post_cell, self.number, self.syntype, self.synclass)

