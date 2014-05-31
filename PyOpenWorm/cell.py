"""
.. class:: Cell

   neuron client
   =============

   This module contains the class that defines the cell

"""

import sqlite3
from rdflib import Graph, Namespace, ConjunctiveGraph, BNode, URIRef, Literal
from rdflib.namespace import RDFS
import PyOpenWorm
from PyOpenWorm import DataObject, DataUser, Configure, propertyTypes
import csv


# XXX: Should we specify somewhere whether we have NetworkX or something else?

class Cell(DataObject):
    def __init__(self, name, conf=False):
        DataObject.__init__(self,conf=conf)
        self._name = name

    def lineageName(self):
        # run some query to get the name
        return ""

    #def rdf(self):

    #def peptides(self):



