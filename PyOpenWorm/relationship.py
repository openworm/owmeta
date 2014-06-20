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
    def __init__(self,triples=[],graph=None,conf=None):
        DataObject.__init__(self,conf=conf)
        if graph:
            self._triples = graph
        else:
            self._triples = triples

    def triples(self):
        for x in self._triples:
            yield x

    def rel(self):
        """
        Returns a set of Relationship objects associated with the call ``class.method_name()``
        :return: Iterable of relationship objects
        """
        #
        attr = getattr(do,name)
        # How to get the appropriate relationship?
        #   need to get the a
