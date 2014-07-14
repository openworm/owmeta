# -*- coding: utf-8 -*-
"""
.. class:: Network

   This module contains the class that defines the neuronal network

"""

import PyOpenWorm as P
import rdflib as R
from PyOpenWorm import DataObject

class Network(DataObject):
    def __init__(self, **kwargs):
        DataObject.__init__(self,**kwargs)
        self.synapses = P.ObjectProperty('synapse',owner=self,value_type=P.Connection)
        P.ObjectProperty('neuron',owner=self,value_type=P.Neuron)

    def neurons(self):
        for x in self.neuron():
            for n in x.name():
                yield n
    def aneuron(self, name, check=False):
        """
        Get a neuron by name

        :param name: Name of a c. elegans neuron
        :returns: Corresponding neuron to the name given
        :rtype: PyOpenWorm.Neuron
        """
        n = P.Neuron(name=name,conf=self.conf)
        if check:
            assert(n.check_exists())
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

        :returns: A list of all sensory neuron names
        :rtype: list
        """

        qres = self['semantic_net'].query(
          """SELECT ?subLabel     #we want to get out the labels associated with the objects
           WHERE {
              ?subject <http://openworm.org/entities/1515> <http://openworm.org/entities/1> . # match all subjects that have the 'is a' (1515) property pointing to 'neuron' (1) or 'interneuron' (2)
              ?subject rdfs:label ?subLabel  #for the subject, look up their plain text label.
            }""")

        for r in qres.result:
            yield str(r[0])

    #def inter(self):

    #def neuroml(self):

    #def rdf(self):

    #def networkx(self):


