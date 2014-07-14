# -*- coding: utf-8 -*-
"""
.. class:: Worm

   This module contains the class that defines the worm as a whole

"""

import PyOpenWorm as P
from PyOpenWorm import DataObject


class Worm(DataObject):

    def __init__(self,**kwargs):
        DataObject.__init__(self,**kwargs)
        P.ObjectProperty("neuron_network", owner=self, value_type=P.Network)
        P.ObjectProperty("muscle", owner=self, value_type=P.Muscle)

    def get_neuron_network(self):
        """
        Get the network object

        :returns: An object to work with the network of the worm
        :rtype: PyOpenWorm.Network
        """
        for x in self.neuron_network():
            return x

    def muscles(self):
        """
        Get all muscles by name

        :returns: A list of all muscle names
        :rtype: list
         """
        for x in self.muscle():
            yield x

    def get_semantic_net(self):
        """
         Get the underlying semantic network as an RDFLib Graph

        :returns: A semantic network containing information about the worm
        :rtype: rdflib.ConjunctiveGraph
         """

        return self['semantic_net']
