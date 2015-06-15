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
    A biological cell.

    All cells with the same name are considered to be the same object.

    Parameters
    -----------
    name : string
        The name of the cell
    lineageName : string
        The lineageName of the cell
        Example::

            >>> c = Cell(name="ADAL")
            >>> c.lineageName() # Returns ["AB plapaaaapp"]

    Attributes
    ----------
    name : DatatypeProperty
        The 'adult' name of the cell typically used by biologists when discussing C. elegans
    lineageName : DatatypeProperty
        The lineageName of the cell

    description : DatatypeProperty
        A description of the cell
    divisionVolume : DatatypeProperty
        When called with no argument, return the volume of the cell at division
        during development.

        When called with an argument, set the volume of the cell at division
        Example::

            >>> v = Quantity("600","(um)^3")
            >>> c = Cell(lineageName="AB plapaaaap")
            >>> c.divisionVolume(v)
    """
    def __init__(self, name=False, lineageName=False, **kwargs):
        DataObject.__init__(self,**kwargs)
        Cell.DatatypeProperty('lineageName',owner=self)
        Cell.DatatypeProperty('name',owner=self)
        Cell.DatatypeProperty('divisionVolume',owner=self)
        Cell.DatatypeProperty('description',owner=self)

        if name:
            self.name(name)

        if lineageName:
            self.lineageName(lineageName)


    def _morphology(self):
        """Return the morphology of the cell. Currently this is restricted to
           `Neuron <#neuron>`_ objects.
        """
        morph_name = "morphology_" + str(next(self.name()))

        # Query for segments
        query = segment_query.substitute(morph_name=morph_name)
        qres = self.rdf.query(query, initNs=ns)
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
        qres = self.rdf.query(query,initNs=ns)
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

    def blast(self):
        """
        Return the blast name.

        Example::

            >>> c = Cell(name="ADAL")
            >>> c.blast() # Returns "AB"

        Note that this isn't a Property. It returns the blast extracted from the ''first''
        lineageName saved.
        """
        import re
        try:
            ln = self.lineageName()
            x = re.split("[. ]", ln)
            return x[0]
        except:
            return ""

    def daughterOf(self):
        """ Return the parent(s) of the cell in terms of developmental lineage.

        Example::

            >>> c = Cell(lineageName="AB plapaaaap")
            >>> c.daughterOf() # Returns [Cell(lineageName="AB plapaaaa")]"""
        ln = self.lineageName()
        parent_ln = ln[:-1]
        return Cell(lineageName=parent_ln)

    def parentOf(self):
        """ Return the direct daughters of the cell in terms of developmental lineage.

        Example::

            >>> c = Cell(lineageName="AB plapaaaap")
            >>> c.parentOf() # Returns [Cell(lineageName="AB plapaaaapp"),Cell(lineageName="AB plapaaaapa")] """
        # XXX: This is pretty icky. We sorely need a convenient way to plug-in
        #      custom patterns to the load query.
        # Alternatively, represent the daughterOf/parentOf relationship with
        # RDF statements rather than making it implicit in the lineageNames

        # hackish. just query for the possible children lineage names...
        ln = self.lineageName()
        possible_child_lns = [ln + "a", ln + "v",
                              ln + "p", ln + "r",
                              ln + "l", ln + "d"]
        for x in possible_child_lns:
            for z in Cell(lineageName=x).load():
                yield z

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

        if self.name.hasValue():
            # name is already set, so we can make an identifier from it
            n = next(self.name._get())
            return self.make_identifier(n)
        else:
            return ident
