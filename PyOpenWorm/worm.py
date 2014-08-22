# -*- coding: utf-8 -*-
"""
.. class:: Worm

   This module contains the class that defines the worm as a whole

"""

import PyOpenWorm
import sqlite3
from rdflib import ConjunctiveGraph, Graph, URIRef, Namespace, Literal
from rdflib.namespace import RDFS


class Worm:

      def __init__(self):
            self.semantic_net = ''
        
      def get_neuron_network(self):
         """
        Get the network object
            
        :returns: An object to work with the network of the worm
        :rtype: PyOpenWorm.Network
       """
         return PyOpenWorm.Network()
             
      def muscles(self):
         """
        Get all muscles by name
            
        :returns: A list of all muscle names
        :rtype: list
         """
         if (self.semantic_net == ''):
             self._init_semantic_net()
    
         qres = self.semantic_net.query(
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
         if (self.semantic_net == ''):
            self._init_semantic_net()
            
         return self.semantic_net
    
      
    
      def _init_semantic_net(self):
         conn = sqlite3.connect('db/celegans.db')
       
         cur = conn.cursor()
    
         #first step, grab all entities and add them to the graph
    
         cur.execute("SELECT DISTINCT ID, Entity FROM tblentity")
    
         n = Namespace("http://openworm.org/entities/")
    
         # print cur.description
    
         g0 = ConjunctiveGraph()
    
         for r in cur.fetchall():
            #first item is a number -- needs to be converted to a string
            first = str(r[0])
            #second item is text 
            second = str(r[1])
            
            # This is the backbone of any RDF graph.  The unique
            # ID for each entity is encoded as a URI and every other piece of 
            # knowledge about that entity is connected via triples to that URI
            # In this case, we connect the common name of that entity to the 
            # root URI via the RDFS label property.
            g0.add( (n[first], RDFS.label, Literal(second)) )
        
    
         #second step, get the relationships between them and add them to the graph
         cur.execute("SELECT DISTINCT EnID1, Relation, EnID2, Citations FROM tblrelationship")
    
         gi = ''    
    
         i = 0
         for r in cur.fetchall():
            #print r
            #all items are numbers -- need to be converted to a string
            first = str(r[0])
            second = str(r[1])
            third = str(r[2])
            prov = str(r[3])
            
            ui = URIRef(u'http://openworm.org/rdfmolecules/' + str(i))
            gi = Graph(g0.store, ui)
        
            gi.add( (n[first], n[second], n[third]) )
            
            g0.add([ui, RDFS.label, Literal(str(i))])
            if (prov is not None):
                g0.add([ui, n[u'text_reference'], Literal(prov)])
                
            i = i + 1
    
         cur.close()
         conn.close()
    
         self.semantic_net = g0