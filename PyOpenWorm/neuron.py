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

	def __init__(self, name):
		
		self._name = name
		self.worm = ''
		self.semantic_net = ''
			
	def _init_networkX(self):
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
		
	def _init_semantic_net(self):
		conn = pymysql.connect(host='my01.winhost.com', port=3306, user='openworm', 
			   passwd='openworm', db='mysql_31129_celegans')
	   
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

		
	def GJ_degree(self):
		"""Get the degree of this neuron for gap junction edges only
		
		:returns: total number of incoming and outgoing gap junctions
		:rtype: int
		"""
		if (self.worm == ''):
			self._init_networkX()
		
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
		
		:returns: total number of incoming and outgoing chemical synapses
		:rtype: int
		"""
		if (self.worm == ''):
			self._init_networkX()
		count = 0
		for item in self.worm.in_edges_iter(self.name(),data=True):
			if 'Send' in item[2]['synapse']:
				count = count + 1
		for item in self.worm.out_edges_iter(self.name(),data=True):
			if 'Send' in item[2]['synapse']:
				count = count + 1
		return count
		
	def type_semantic(self):
		if (self.semantic_net == ''):
			self._init_semantic_net()
		
		print("going to get results...")
	
		qres = self.semantic_net.query(
		  """SELECT ?objLabel     #we want to get out the labels associated with the predicates and the objects
		   WHERE {
			  ?node ?p '"""+self.name()+"""' .   #we are looking first for the 'AVALnode' that is the anchor of all information about the AVAL neuron
			  ?node <http://openworm.org/entities/1515> ?object .# having identified that node, here we match any predicate and object associated with the AVALnode
			  ?object rdfs:label ?objLabel  #for the object, look up their plain text label.
			}""")       
	
		type = ''
		for r in qres.result:
			type = str(r[0])
		
		return type
		
	def type_networkX(self):
		if (self.worm == ''):
			self._init_networkX()
		return self.worm.node[self.name()]['ntype']		

	def type(self):
		"""Get type of this neuron (motor, interneuron, sensory)
			
		:returns: the type
		:rtype: str
		"""
		return self.type_networkX().lower()
		
	def name(self):
		"""Get name of this neuron (e.g. AVAL)
			
		:returns: the name
		:rtype: str
		"""
		return self._name
	
	
	# This method can start out life by reading in the nml files
	# from GitHub
	#def as_neuroml(self):
	#   """Return this neuron as a NeuroML representation
	#	:rtype: str
	#   """
	
	#def rdf(self):
	
	#def channels(self):
	
	#def peptides(self):
	
	