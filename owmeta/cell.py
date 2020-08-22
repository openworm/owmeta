from __future__ import print_function

from owmeta_core.dataobject import DatatypeProperty, ObjectProperty, This

from .channel import Channel
from .biology import BiologyType
from .cell_common import CELL_RDF_TYPE


class Cell(BiologyType):
    """
    A biological cell.

    All cells with the same `name` are considered to be the same object.

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

    key_property = {'property': name, 'type': 'direct'}

    def __init__(self, name=None, lineageName=None, **kwargs):
        # NOTE: We name the `name` and `lineageName` as positional parameters for
        # convenience
        super(Cell, self).__init__(name=name, lineageName=lineageName, **kwargs)

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