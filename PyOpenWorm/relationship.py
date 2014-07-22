"""
.. class:: Relationship

   relationship
   =============

   Relationships relate two or more DataObjects

"""
from PyOpenWorm import DataObject

# Relationships correspond to a subgraph in the database.
# Consequently, they can be reduced to or built up from a
#  set of triples.
class Relationship(DataObject):
    def __init__(self,triples=[],graph=None,**kwargs):
        DataObject.__init__(self,**kwargs)
        if graph:
            self._triples = graph
        else:
            self._triples = triples
