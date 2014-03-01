# -*- coding: utf-8 -*-

import unittest

import PyOpenWorm
import networkx
import rdflib


class PyOpenWormTest(unittest.TestCase):
    """Test for PyOpenWorm."""

    def test_network(self):
        self.assertTrue(isinstance(PyOpenWorm.Network(),PyOpenWorm.Network))
        
    def test_network_aneuron(self):
    	  self.assertTrue(isinstance(PyOpenWorm.Network().aneuron('AVAL'),PyOpenWorm.Neuron))
   
    def test_network_neurons(self):
   	  self.assertTrue('AVAL' in PyOpenWorm.Network().neurons())
   	  self.assertTrue('DD5' in PyOpenWorm.Network().neurons())
   	  self.assertEquals(len(PyOpenWorm.Network().neurons()), 302)
   		
    def test_worm_muscles(self):
   	  self.assertTrue('MDL08' in PyOpenWorm.Worm().muscles())
   	  self.assertTrue('MDL15' in PyOpenWorm.Worm().muscles())
    	
    def test_neuron_type(self):
    	  self.assertEquals(PyOpenWorm.Network().aneuron('AVAL').type(),'interneuron')
    	  self.assertEquals(PyOpenWorm.Network().aneuron('DD5').type(),'motor')
    	  self.assertEquals(PyOpenWorm.Network().aneuron('PHAL').type(),'sensory')
    	
    def test_neuron_name(self):
    	  self.assertEquals(PyOpenWorm.Network().aneuron('AVAL').name(),'AVAL')
    	  self.assertEquals(PyOpenWorm.Network().aneuron('AVAR').name(),'AVAR')
    	
    def test_neuron_GJ_degree(self):
    	  self.assertEquals(PyOpenWorm.Network().aneuron('AVAL').GJ_degree(),60)
    	
    def test_neuron_Syn_degree(self):
    	  self.assertEquals(PyOpenWorm.Network().aneuron('AVAL').Syn_degree(),74)
    	
    def test_network_as_networkx(self):
    	  self.assertTrue(isinstance(PyOpenWorm.Network().as_networkx(),networkx.DiGraph))
        
    def test_neuron_receptors(self):
	  self.assertTrue('GLR-2' in PyOpenWorm.Neuron('AVAL').receptors())
	  self.assertTrue('OSM-9' in PyOpenWorm.Neuron('PHAL').receptors())
  
    def test_worm_get_network(self):
        self.assertTrue(isinstance(PyOpenWorm.Worm().get_neuron_network(), PyOpenWorm.Network))
        
    def test_worm_get_semantic_net(self):
        g0 = PyOpenWorm.Worm().get_semantic_net()        
        self.assertTrue(isinstance(g0, rdflib.ConjunctiveGraph))
        
        qres = g0.query(
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
        list = []
        for r in qres.result:
            list.append(str(r[0]))
        self.assertTrue('MDL08' in list)
   
    def test_neuron_get_reference(self):
        self.assertEquals(PyOpenWorm.Neuron('ADER').get_reference(0,'EXP-1'), ['http://dx.doi.org/10.100.123/natneuro'])
        self.assertEquals(PyOpenWorm.Neuron('ADER').get_reference(0,'DOP-2'), None)
		
    def test_muscle(self):
        self.assertTrue(isinstance(PyOpenWorm.Muscle('MDL08'),PyOpenWorm.Muscle))


