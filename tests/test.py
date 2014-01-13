# -*- coding: utf-8 -*-

import unittest

import PyOpenWorm


class PyOpenWormTest(unittest.TestCase):
    """Test for PyOpenWorm."""

    def test_network(self):
        self.assertTrue(isinstance(PyOpenWorm.Network(),PyOpenWorm.Network))
        
    def test_network_aneuron(self):
    	self.assertTrue(isinstance(PyOpenWorm.Network().aneuron('AVAL'),PyOpenWorm.Neuron))
    	
    def test_neuron_type(self):
    	self.assertEquals(PyOpenWorm.Network().aneuron('AVAL').type(),'Interneuron')
    	
    def test_neuron_name(self):
    	self.assertEquals(PyOpenWorm.Network().aneuron('AVAL').name(),'AVAL')
        
#    def test_bneuron(self):
#        self.assertTrue(1)

        