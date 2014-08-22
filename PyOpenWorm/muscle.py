"""
.. class:: Muscle

   muscle client
   =============

   This module contains the class that defines the muscle

"""

import sqlite3
from rdflib import Graph
from rdflib import Namespace
from rdflib.namespace import RDF, RDFS
from rdflib import URIRef, BNode, Literal
import urllib2
import networkx as nx
import csv

class Muscle:

	def __init__(self, name):
		self._name = name

	def name(self):
		"""Get name of this muscle
			
		:returns: the name
		:rtype: str
		"""
		return self._name

	def _receptors(self):
		"""Get receptors associated with this muscle
			
		:returns: a list of all known receptors
		:rtype: list
		"""
		if (self.semantic_net == ''):
			self._init_semantic_net()

		qres = self.semantic_net.query(
		  """SELECT ?objLabel     #we want to get out the labels associated with the objects
		   WHERE {
			  ?node ?p '"""+self.name()+"""' .   #we are looking first for the node that is the anchor of all information about the specified muscle
			  ?node <http://openworm.org/entities/361> ?object .# having identified that node, here we match an object associated with the node via the 'receptor' property (number 361)
			  ?object rdfs:label ?objLabel  #for the object, look up their plain text label.
			}""")       

		receptors = []
		for r in qres.result:
			receptors.append(str(r[0]))

		return receptors


