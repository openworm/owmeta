# -*- coding: utf-8 -*-
"""
.. class:: Network

   This module contains the class that defines the neuronal network

"""

import PyOpenWorm

class Network(PyOpenWorm.Configure):

    def __init__(self,conf=False):
        PyOpenWorm.Configure.__init__(self,conf)

    def aneuron_nocheck(self, name):
        """
        Get a neuron by name

        :param name: Name of a c. elegans neuron
        :returns: Corresponding neuron to the name given
        :rtype: PyOpenWorm.Neuron
        """
        return PyOpenWorm.Neuron(name,self)

    def aneuron(self, name):
        """
        Get a neuron by name

        :param name: Name of a c. elegans neuron
        :returns: Corresponding neuron to the name given
        :rtype: PyOpenWorm.Neuron
        """
        n = PyOpenWorm.Neuron(name,self)
        assert(n.check_exists())
        return n

    def neurons(self):
        """
        Get all neurons by name

        :returns: A list of all neuron names
        :rtype: list
        """

        qres = self['semantic_net'].query(
          """SELECT ?subLabel     #we want to get out the labels associated with the objects
           WHERE {
              ?subject <http://openworm.org/entities/1515> <http://openworm.org/entities/1> .# match all subjects that have the 'is a' (1515) property pointing to 'neuron' (1)
              ?subject rdfs:label ?subLabel  #for the subject, look up their plain text label.
            }""")

        neurons = []
        for r in qres.result:
            neurons.append(str(r[0]))

        return neurons

    def as_networkx(self):
        return self['nx']

    #def sensory(self):

    #def inter(self):

    #def neuroml(self):

    #def rdf(self):

    #def networkx(self):


