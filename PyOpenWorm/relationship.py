from __future__ import print_function
from itertools import chain
from .dataObject import DataObject

# Relationships correspond to a subgraph in the database.
# Consequently, they can be reduced to or built up from a
#  set of triples.
class Relationship(DataObject):
    """Relationships relate two or more DataObjects
    """
    def __init__(self,triples=None,graph=None,**kwargs):
        super(DataObject,self).__init__(**kwargs)
        if triples is None:
            triples = []

        if graph is not None:
            self._triples = []
            for trip in graph:
                self._triples.append(trip)
        else:
            self._triples = triples

    def identifier(self):
        data = sorted(self._triples)
        if len(data) == 0:
            return None
        else:
            res = 1
            for x in data:
                res = 31*res + hash(tuple(x))
            return self.make_identifier(res)
