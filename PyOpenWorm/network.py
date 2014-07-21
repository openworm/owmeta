# -*- coding: utf-8 -*-
"""
.. class:: Network

   This module contains the class that defines the neuronal network

"""

import PyOpenWorm as P
import rdflib as R
from PyOpenWorm import DataObject

class Network(DataObject):
    """
    Attributes
    ----------
    neuron : ObjectProperty
        Representation of neurons in the network
    synapse : ObjectProperty
        Representation of synapses in the network
    """
    def __init__(self, **kwargs):
        DataObject.__init__(self,**kwargs)
        self.synapses = P.ObjectProperty('synapse',owner=self,value_type=P.Connection)
        P.ObjectProperty('neuron',owner=self,value_type=P.Neuron)

    def neurons(self):
        for x in self.neuron():
            for n in x.name():
                yield n
    def aneuron(self, name):
        """
        Get a neuron by name

        :param name: Name of a c. elegans neuron
        :returns: Neuron corresponding to the name given
        :rtype: PyOpenWorm.Neuron
        """
        n = P.Neuron(name=name,conf=self.conf)
        return n

    def _synapses_csv(self):
        """
        Get all synapses by

        :returns: A generator of Connection objects
        :rtype: generator
        """
        for n,nbrs in self['nx'].adjacency_iter():
            for nbr,eattr in nbrs.items():
                yield P.Connection(n,nbr,int(eattr['weight']),eattr['synapse'],eattr['neurotransmitter'],conf=self.conf)

    def as_networkx(self):
        return self['nx']

    def sensory(self):
        """
        Get all sensory neurons by name

        :returns: A iterable of all sensory neurons
        :rtype: iter(Neuron)
        """

        # TODO: make sure these belong to *this* Network
        n = P.Neuron()
        n.type('sensory')

        for x in n.load():
            yield x
    def interneurons(self):
        """
        Get all interneurons neurons

        :returns: A iterable of all interneurons
        :rtype: iter(Neuron)
        """

        # TODO: make sure these belong to *this* Network
        n = P.Neuron()
        n.type('interneuron')

        for x in n.load():
            yield x

    #def neuroml(self):

    #def rdf(self):

    #def networkx(self):


