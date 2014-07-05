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

    @classmethod
    def rel(self, the_class, the_method):
        """
        Returns a set of Relationship objects associated with the call ``class.method_name()``
        :return: Iterable of relationship objects
        """
        assert(issubclass(the_class, DataObject))
        attr = getattr(the_class,the_method)
        # How to get the appropriate relationship?
        #   need to get the a
