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
import urllib2
import networkx as nx
import csv

class Neuron:

	def __init__(self):
		
		self.worm = nx.DiGraph()
		
		# Neuron table
		csvfile = urllib2.urlopen('https://raw.github.com/openworm/data-viz/master/HivePlots/neurons.csv')
		
		reader = csv.reader(csvfile, delimiter=';', quotechar='|')
		for row in reader:
			neurontype = ""
			# Detects neuron function
			if "sensory" in row[1].lower():
				neurontype += "sensory"
			if "motor" in row[1].lower():
				neurontype += "motor"    
			if "interneuron" in row[1].lower():
				neurontype += "interneuron"
			if len(neurontype) == 0:
				neurontype = "unknown"
				
			if len(row[0]) > 0: # Only saves valid neuron names
				self.worm.add_node(row[0], ntype = neurontype)
		
		# Connectome table
		csvfile = urllib2.urlopen('https://raw.github.com/openworm/data-viz/master/HivePlots/connectome.csv')
		
		reader = csv.reader(csvfile, delimiter=';', quotechar='|')
		for row in reader:
			self.worm.add_edge(row[0], row[1], weight = row[3])
			self.worm[row[0]][row[1]]['synapse'] = row[2]
			self.worm[row[0]][row[1]]['neurotransmitter'] = row[4]
		
	def GJ_degree(self):
		"""Get the degree of this neuron for gap junction edges only
		
		:returns: total number of incoming and outgoing synapses
		:rtype: int
		"""
		count = 0
		for item in self.worm.in_edges_iter(self.name(),data=True):
			if 'GapJunction' in item[2]['synapse']:
				count = count + 1
		for item in self.worm.out_edges_iter(self.name(),data=True):
			if 'GapJunction' in item[2]['synapse']:
				count = count + 1
		return count
	
	
	def Syn_degree(self):
		"""Get the degree of a this neuron for chemical synapse edges only
		
		:returns: total number of incoming and outgoing synapses
		:rtype: int
		"""
		count = 0
		for item in self.worm.in_edges_iter(self.name(),data=True):
			if 'Send' in item[2]['synapse']:
				count = count + 1
		for item in self.worm.out_edges_iter(self.name(),data=True):
			if 'Send' in item[2]['synapse']:
				count = count + 1
		return count
		

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
	
	