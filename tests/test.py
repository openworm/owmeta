# -*- coding: utf-8 -*-

import unittest

import PyOpenWorm
import networkx


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
   		
   	def test_network_muscles(self):
   		self.assertTrue('MDL08' in PyOpenWorm.Network().muscles())
   		self.assertTrue('MDL15' in PyOpenWorm.Network().muscles())
    	
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
		
    def test_muscle(self):
        self.assertTrue(isinstance(PyOpenWorm.Muscle(),PyOpenWorm.Muscle))
        
        def test_muscle_receptors(self):
		self.assertTrue('UNC-68' in PyOpenWorm.Muscle('MDL08').receptors())

        
