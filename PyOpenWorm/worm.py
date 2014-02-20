# -*- coding: utf-8 -*-
"""
.. class:: Worm

   This module contains the class that defines the worm as a whole

"""

import PyOpenWorm

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
	
	