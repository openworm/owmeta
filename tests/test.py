# -*- coding: utf-8 -*-

import unittest

import PyOpenWorm


class PyOpenWormTest(unittest.TestCase):
    """Test for PyOpenWorm."""

    def test_network(self):
        self.assertTrue(isinstance(PyOpenWorm.Network(),PyOpenWorm.Network))
        
    def test_network_aneuron(self):
    	self.assertTrue(isinstance(PyOpenWorm.Network().aneuron('AVAL'),PyOpenWorm.Neuron))
        
#    def test_bneuron(self):
#        self.assertTrue(1)

        