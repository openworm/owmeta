from __future__ import print_function

from string import Template
import neuroml

from .channel import Channel
from .biology import BiologyType
from .dataObject import DatatypeProperty, ObjectProperty, This
from .cell_common import CELL_RDF_TYPE

__all__ = ["Cell"]

# XXX: Should we specify somewhere whether we have NetworkX or something else?
ns = {'ns1': 'http://www.neuroml.org/schema/neuroml2/'}
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


def _dict_merge(d1, d2):
    from itertools import chain
    dict(chain(d1.items(), d2.items()))


class Cell(BiologyType):

    """
    A biological cell.

    All cells with the same name are considered to be the same object.

    Parameters
    -----------
    name : str
        The name of the cell
    lineageName : str
        The lineageName of the cell
    """

    class_context = BiologyType.class_context

    rdf_type = CELL_RDF_TYPE

    divisionVolume = DatatypeProperty()
    ''' The volume of the cell at division

        Example::

            >>> v = Quantity("600","(um)^3")
            >>> c = Cell(lineageName="AB plapaaaap")
            >>> c.divisionVolume(v)
    '''

    name = DatatypeProperty()
    ''' The 'adult' name of the cell typically used by biologists when discussing C. elegans '''
    wormbaseID = DatatypeProperty()

    description = DatatypeProperty()
    ''' A description of the cell '''

    channel = ObjectProperty(value_type=Channel,
                             multiple=True,
                             inverse_of=(Channel, 'appearsIn'))

    lineageName = DatatypeProperty()
    ''' The lineageName of the cell
        Example::

            >>> c = Cell(name="ADAL")
            >>> c.lineageName() # Returns ["AB plapaaaapp"]
    '''

    synonym = DatatypeProperty(multiple=True)
    daughterOf = ObjectProperty(value_type=This,
                                inverse_of=(This, 'parentOf'))
    parentOf = ObjectProperty(value_type=This, multiple=True)

    def __init__(self, name=None, lineageName=None, **kwargs):
        super(Cell, self).__init__(**kwargs)
        if name:
            self.name(name)

        if lineageName:
            self.lineageName(lineageName)

    def _morphology(self):
        """Return the morphology of the cell. Currently this is restricted to
           `Neuron <#neuron>`_ objects.
        """
        morph_name = "morphology_" + str(self.name())

        # Query for segments
        query = segment_query.substitute(morph_name=morph_name)
        qres = self.rdf.query(query, initNs=ns)
        morph = neuroml.Morphology(id=morph_name)
        for r in qres:
            par = False

            if r['par_id']:
                par = neuroml.SegmentParent(segments=str(r['par_id']))
                s = neuroml.Segment(name=str(r['seg_name']),
                                    id=str(r['seg_id']), parent=par)
            else:
                s = neuroml.Segment(name=str(r['seg_name']),
                                    id=str(r['seg_id']))

            if r['x_prox']:
                loop_prox = neuroml.Point3DWithDiam(*(r[x] for x
                                                      in ['x_prox',
                                                          'y_prox',
                                                          'z_prox',
                                                          'd_prox']))
                s.proximal = loop_prox

            loop = neuroml.Point3DWithDiam(*(r[x] for x in ['x',
                                                            'y',
                                                            'z',
                                                            'd']))
            s.distal = loop
            morph.segments.append(s)
        # Query for segment groups
        query = segment_group_query.substitute(morph_name=morph_name)
        qres = self.rdf.query(query, initNs=ns)
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

    def blast(self):
        """
        Return the blast name.

        Example::

            >>> c = Cell(name="ADAL")
            >>> c.blast() # Returns "AB"

        Note that this isn't a Property. It returns the blast extracted from
        the ''first'' lineageName saved.
        """
        import re
        try:
            ln = self.lineageName()
            x = re.split("[. ]", ln)
            return x[0]
        except Exception:
            return ""

    def __str__(self):
        if self.name.has_defined_value():
            return str(self.name.defined_values[0].idl)
        else:
            return super(Cell, self).__str__()

    def defined_augment(self):
        return self.name.has_defined_value()

    def identifier_augment(self, *args, **kwargs):
        return self.make_identifier_direct(str(self.name.defined_values[0].identifier))


__yarom_mapped_classes__ = (Cell,)
