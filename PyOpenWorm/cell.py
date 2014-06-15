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
from PyOpenWorm import DataObject
import neuroml


# XXX: Should we specify somewhere whether we have NetworkX or something else?

class Cell(DataObject):
    def __init__(self, name, conf=False):
        DataObject.__init__(self,conf=conf)
        self._name = name

    def lineageName(self):
        # run some query to get the name
        return ""

    def morphology(self):
        morph_name="morphology_" + str(self.name())
        ns =  {'ns1': 'http://www.neuroml.org/schema/neuroml2/'}

        # Query for segments
        qres = self['semantic_net'].query(
          """
          SELECT ?seg_id ?seg_name ?x ?y ?z ?d ?par_id ?x_prox ?y_prox ?z_prox ?d_prox
           WHERE {
              ?p ns1:id 'morphology_AFDL' .
              ?p ns1:segment ?segment .
              ?segment ns1:distal 	?loop
                     ; ns1:id 	    ?seg_id
                     ; ns1:name 	?seg_name .

              OPTIONAL {
                  ?segment ns1:proximal	?loop_prox .
                  ?loop_prox ns1:x ?x_prox
                    ; ns1:y ?y_prox
                    ; ns1:z ?z_prox
                    ; ns1:diameter ?d_prox .
              }
              OPTIONAL {?segment ns1:parent ?par . ?par ns1:segment ?par_id  }.
              ?loop ns1:x ?x
                ; ns1:y ?y
                ; ns1:z ?z
                ; ns1:diameter ?d .
            }
            """,initNs=ns)
        # Query for segment groups
        morph = neuroml.Morphology(id=morph_name)
        for r in qres:
            par = False

            if r['par_id']:
                par = neuroml.SegmentParent(segments=int(r['par_id']))
                s = neuroml.Segment(name=r['seg_name'], id=r['seg_id'], parent=par)
            else:
                s = neuroml.Segment(name=r['seg_name'], id=r['seg_id'])

            if r['x_prox']:
                loop_prox = neuroml.Point3DWithDiam(*(r[x] for x in ['x_prox','y_prox','z_prox','d_prox']))
                s.proximal = loop_prox

            loop = neuroml.Point3DWithDiam(*(r[x] for x in ['x','y','z','d']))
            s.distal = loop
            morph.segments.append(s)
        # Query for segment groups
        qres = self['semantic_net'].query(
          """
          SELECT ?gid ?member ?include
           WHERE {
              ?p ns1:id 'morphology_AFDL' .
              ?p ns1:segmentGroup ?seg_group .
              ?seg_group ns1:id ?gid .
              OPTIONAL {
                ?seg_group ns1:include ?inc .
                ?inc ns1:segmentGroup ?include .
              }
              OPTIONAL {
                ?seg_group ns1:member ?inc .
                ?inc ns1:segment ?member .
              }
            }
            """,initNs=ns)
        for r in qres:
            s = neuroml.SegmentGroup(id=r['gid'])
            if r['member']:
                m = neuroml.Member()
                m.segments = str(r['member'])
                s.members.append(m)
            elif r['include']:
                i = neuroml.Include()
                i.segment_groups = str(r['include'])
                s.includes.append(i)
            morph.segment_groups.append(s)
        return morph

    def name(self):
        return self._name
    #def rdf(self):

    #def peptides(self):



