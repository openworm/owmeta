# -*- coding: utf-8 -*-
"""
.. class:: Network

   This module contains the class that defines the neuronal network

"""

import PyOpenWorm
import rdflib as R
from PyOpenWorm import DataObject

class Network(DataObject):
    def __init__(self, conf=False):
        DataObject.__init__(self,conf=conf)

    def identifier(self):
        return self.conf['rdf.namespace']['worm_net']

    def aneuron(self, name, check=False):
        """
        Get a neuron by name

        :param name: Name of a c. elegans neuron
        :returns: Corresponding neuron to the name given
        :rtype: PyOpenWorm.Neuron
        """
        n = PyOpenWorm.Neuron(name,self.conf)
        if check:
            assert(n.check_exists())
        return n

    def neurons(self):
        """
        Get all neurons by name

        :returns: A list of all neuron names
        :rtype: list
        """

        qres = self['semantic_net'].query(
          """SELECT DISTINCT ?subLabel     #we want to get out the labels associated with the objects
           WHERE {
              {
                  ?subject <http://openworm.org/entities/1515> <http://openworm.org/entities/1> . # match all subjects that have the 'is a' (1515) property pointing to 'neuron' (1) or 'interneuron' (2)
              }
              UNION
              {
                  ?subject <http://openworm.org/entities/1515> <http://openworm.org/entities/2> .
              }
              ?subject rdfs:label ?subLabel  #for the subject, look up their plain text label.
            }""")

        for r in qres.result:
            yield str(r[0])

    def synapses(self):
        """
        Get all synapses by

        :returns: A generator of Connection objects
        :rtype: generator
        """
        for x in self._synapses_csv():
            yield x

    def _synapses_csv(self):
        """
        Get all synapses by

        :returns: A generator of Connection objects
        :rtype: generator
        """
        for n,nbrs in self['nx'].adjacency_iter():
            for nbr,eattr in nbrs.items():
                yield PyOpenWorm.Connection(n,nbr,int(eattr['weight']),eattr['synapse'],eattr['neurotransmitter'],conf=self.conf)

    def _synapses_rdf(self):
        """
        Get all synapses by

        :returns: A generator of Connection objects
        :rtype: generator
        """
        # It only makes sense to talk about _all_ of the connections...so we should just get all of the connections
        for x in PyOpenWorm.Connection().load():
            yield x

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


