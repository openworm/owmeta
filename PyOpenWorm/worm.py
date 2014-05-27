# -*- coding: utf-8 -*-
"""
.. class:: Worm

   This module contains the class that defines the worm as a whole

"""

import PyOpenWorm
from PyOpenWorm import Configureable


class Worm(Configureable):

    def __init__(self,conf=False):
        Configureable.__init__(self,conf)

    def get_neuron_network(self):
        """
        Get the network object

        :returns: An object to work with the network of the worm
        :rtype: PyOpenWorm.Network
       """
        return PyOpenWorm.Network(self.conf)

    def muscles(self):
        """
        Get all muscles by name

        :returns: A list of all muscle names
        :rtype: list
         """

        qres = self['semantic_net_new'].query(
                 """
          SELECT ?subLabel     #we want to get out the labels associated with the objects
            WHERE {
              GRAPH ?g { #Each triple is in its own sub-graph to enable provenance
                # match all subjects that have the 'is a' (1515) property pointing to 'muscle' (1519)
                ?subject <http://openworm.org/entities/1515> <http://openworm.org/entities/1519> .
                }
              #Triples that have the label are in the main graph only
              ?subject rdfs:label ?subLabel  #for the subject, look up their plain text label.
            }
          """)

        muscles = []
        for r in qres.result:
            muscles.append(str(r[0]))

        return muscles

    def get_semantic_net(self):
        """
         Get the underlying semantic network as an RDFLib Graph

        :returns: A semantic network containing information about the worm
        :rtype: rdflib.ConjunctiveGraph
         """

        return self['semantic_net']
