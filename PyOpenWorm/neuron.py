"""
.. class:: Neuron

neuron client
=============

This module contains the class that defines the neuron

"""

import pymysql
from rdflib import Graph
from rdflib import Namespace
from rdflib.namespace import RDF, RDFS
from rdflib import URIRef, BNode, Literal
import urllib

class Neuron:

	def type(self):
		"""Get type of this neuron (motor, interneuron, sensory)
			
		:returns: the type
		:rtype: str
		"""
		return 'Interneuron'
		
	def name(self):
		"""Get name of this neuron (e.g. AVAL)
			
		:returns: the name
		:rtype: str
		"""
		return 'AVAL'
	
	
	#def neuroml(self):
	
	#def rdf(self):
	
	#def channels(self):
	
	#def peptides(self):
	
	