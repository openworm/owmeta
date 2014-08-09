"""
.. class:: Connection

   connection
   =============

   Connection between neurons

"""
import PyOpenWorm as P
from PyOpenWorm import *

__all__ = ['Connection']

class SynapseType:
    Chemical = "send"
    GapJunction = "gapJunction"
class Connection(Relationship):
    """Connection between neurons

    Parameters
    ----------
    pre_cell : string or Neuron, optional
        The pre-synaptic cell
    post_cell : string or Neuron, optional
        The post-synaptic cell
    number : int, optional
        The weight of the connection
    syntype : {'gapJunction', 'send'}, optional
        The kind of synaptic connection. 'gapJunction' indicates
        a gap junction and 'send' a chemical synapse
    synclass : string, optional
        The kind of Neurotransmitter (if any) sent between `pre_cell` and `post_cell`
    """
    datatypeProperties = ['syntype',
            'synclass',
            'number',]
    objectProperties = [('pre_cell',P.Neuron),
            ('post_cell',P.Neuron)]

    def __init__(self,
                 pre_cell=None,
                 post_cell=None,
                 number=None,
                 syntype=None,
                 synclass=None,
                 **kwargs):
        Relationship.__init__(self,**kwargs)

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
