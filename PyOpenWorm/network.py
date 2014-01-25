# -*- coding: utf-8 -*-
"""
.. class:: Network

   This module contains the class that defines the network

"""

import pymysql
from rdflib import Graph
from rdflib import Namespace
from rdflib.namespace import RDF, RDFS
from rdflib import URIRef, BNode, Literal
import urllib, urllib2
import PyOpenWorm
import networkx as nx
import csv

class Network:

	#def __init__(self):
	
#	def motor(self):
#		return motor
	
	def aneuron(self, name):
		"""
		Get a neuron by name
			
		:param name: Name of a c. elegans neuron
		:returns: Corresponding neuron to the name given
		:rtype: PyOpenWorm.Neuron
		"""
		return PyOpenWorm.Neuron(name)

	def as_networkx(self):
		"""
		Get the network represented as a `NetworkX <http://networkx.github.io/documentation/latest/>`_ graph
			
		Nodes include neuron name and neuron type.  Edges include kind of synapse and neurotransmitter.
			
		:returns: directed graphs with neurons as verticies and gap junctions and chemical synapses as edges
		:rtype: `NetworkX.DiGraph <http://networkx.github.io/documentation/latest/reference/classes.digraph.html?highlight=digraph#networkx.DiGraph>`_
		"""
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
			
		return self.worm
		
	#def sensory(self):
	
	#def inter(self):
	
	#def neuroml(self):
	
	#def rdf(self):
	
	#def networkx(self):
	
	