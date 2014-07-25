"""
.. class:: Cell

   cell client
   =============

   This module contains the class that defines the cell

"""

from PyOpenWorm import *
from string import Template
import neuroml
__all__ = [ "Cell" ]

# XXX: Should we specify somewhere whether we have NetworkX or something else?
ns =  {'ns1': 'http://www.neuroml.org/schema/neuroml2/'}
segment_query = Template("""
SELECT ?seg_id ?seg_name ?x ?y ?z ?d ?par_id ?x_prox ?y_prox ?z_prox ?d_prox
WHERE {
  ?p ns1:id '$morph_name' .
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
            """)
segment_group_query = Template("""
SELECT ?gid ?member ?include
WHERE {
  ?p ns1:id '$morph_name' .
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
            """)
def _dict_merge(d1,d2):
    from itertools import chain
    dict(chain(d1.items(), d2.items()))

class Cell(DataObject):
    """
    A biological cell

    Parameters
    -----------
    name : string
        The name of the cell
    lineageName : string
        The lineageName of the cell

    Attributes
    ----------
    name : DatatypeProperty
        The name of the cell
    lineageName : DatatypeProperty
        The lineageName of the cell
    """
    def __init__(self, name=False, lineageName=False, **kwargs):
        DataObject.__init__(self,**kwargs)
        DatatypeProperty('lineageName',owner=self)
        DatatypeProperty('name',owner=self)

        if name:
            self.name(name)

        if lineageName:
            self.lineageName(lineageName)

    def morphology(self):
        morph_name = "morphology_" + str(next(self.name()))

        # Query for segments
        query = segment_query.substitute(morph_name=morph_name)
        qres = self['semantic_net'].query(query, initNs=ns)
        morph = neuroml.Morphology(id=morph_name)
        for r in qres:
            par = False

            if r['par_id']:
                par = neuroml.SegmentParent(segments=str(r['par_id']))
                s = neuroml.Segment(name=str(r['seg_name']), id=str(r['seg_id']), parent=par)
            else:
                s = neuroml.Segment(name=str(r['seg_name']), id=str(r['seg_id']))

            if r['x_prox']:
                loop_prox = neuroml.Point3DWithDiam(*(r[x] for x in ['x_prox','y_prox','z_prox','d_prox']))
                s.proximal = loop_prox

            loop = neuroml.Point3DWithDiam(*(r[x] for x in ['x','y','z','d']))
            s.distal = loop
            morph.segments.append(s)
        # Query for segment groups
        query = segment_group_query.substitute(morph_name=morph_name)
        qres = self['semantic_net'].query(query,initNs=ns)
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
    def __eq__(self,other):
        return DataObject.__eq__(self,other) or (isinstance(other,Cell) and set(self.name()) == set(other.name()))

    def identifier(self, *args, **kwargs):
        # If the DataObject identifier isn't variable, then self is a specific
        # object and this identifier should be returned. Otherwise, if our name
        # attribute is _already_ set, then we can get the identifier from it and
        # return that. Otherwise, there's no telling from here what our identifier
        # should be, so the variable identifier (from DataObject.identifier() must
        # be returned
        ident = DataObject.identifier(self, *args, **kwargs)
        if 'query' in kwargs and kwargs['query'] == True:
            if not DataObject._is_variable(ident):
                return ident

            if len(self.name.v) > 0:
                # name is already set, so we can make an identifier from it
                n = next(self.name())
                return self.make_identifier(n)
            else:
                return ident
        else:
            if len(self.name.v) > 0:
                # name is already set, so we can make an identifier from it
                n = next(self.name())
                return self.make_identifier(n)
            else:
                return ident

    #def rdf(self):

    #def peptides(self):



