from PyOpenWorm import DataObject

# Relationships correspond to a subgraph in the database.
# Consequently, they can be reduced to or built up from a
#  set of triples.
class Relationship(DataObject):
    """Relationships relate two or more DataObjects
    """
    def __init__(self,triples=None,graph=None,**kwargs):
        DataObject.__init__(self,**kwargs)
        if triples is None:
            triples = []

        if graph is not None:
            self._triples = graph
        else:
            self._triples = triples
