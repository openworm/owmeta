# -*- coding: utf-8 -*-
"""
.. class:: Network

   This module contains the class that defines the neuronal network

"""

import sqlite3
from rdflib import Graph
from rdflib import Namespace
from rdflib.namespace import RDFS
from rdflib import Literal
import urllib2
import PyOpenWorm
import networkx as nx
import csv

class Network:

	def __init__(self):
		self.networkX = ''
		self.semantic_net = ''
	
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

	def neurons(self):
		"""
		Get all neurons by name
			
		:returns: A list of all neuron names
		:rtype: list
		"""
		if (self.semantic_net == ''):
			self._init_semantic_net()
	
		qres = self.semantic_net.query(
		  """SELECT ?subLabel     #we want to get out the labels associated with the objects
		   WHERE {
			  ?subject <http://openworm.org/entities/1515> <http://openworm.org/entities/1> .# match all subjects that have the 'is a' (1515) property pointing to 'neuron' (1)
			  ?subject rdfs:label ?subLabel  #for the subject, look up their plain text label.
			}""")       
	
		neurons = []
		for r in qres.result:
			neurons.append(str(r[0]))
			
		return neurons
	
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
		
	def _init_semantic_net(self):
		conn = sqlite3.connect('db/celegans.db')
	   
		cur = conn.cursor()
	
		#first step, grab all entities and add them to the graph
	
		cur.execute("SELECT DISTINCT ID, Entity FROM tblentity")
	
		n = Namespace("http://openworm.org/entities/")
	
		# print cur.description
	
		g = Graph()
	
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
			g.add( (n[first], RDFS.label, Literal(second)) )
	
		#second stem, get the relationships between them and add them to the graph
		cur.execute("SELECT DISTINCT EnID1, Relation, EnID2 FROM tblrelationship")
	
		for r in cur.fetchall():
			#print r
			#all items are numbers -- need to be converted to a string
			first = str(r[0])
			second = str(r[1])
			third = str(r[2])
		
			g.add( (n[first], n[second], n[third]) )
	
		cur.close()
		conn.close()
	
		self.semantic_net = g
		
	#def sensory(self):
	
	#def inter(self):
	
	#def neuroml(self):
	
	#def rdf(self):
	
	#def networkx(self):
	
	