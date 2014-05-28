"""
.. class:: Muscle

   muscle client
   =============

   This module contains the class that defines the muscle

"""
import PyOpenWorm
from PyOpenWorm import DataUser

class Muscle(DataUser):

    def __init__(self, name, conf=False):
        DataUser.__init__(self,conf)
        self._name = name

    def name(self):
        """Get name of this muscle

        :returns: the name
        :rtype: str
        """
        return self._name

    def receptors(self):
        """Get receptors associated with this muscle

        :returns: a list of all known receptors
        :rtype: list
        """

        qres = self['semantic_net'].query(
                """SELECT ?objLabel     #we want to get out the labels associated with the objects
           WHERE {
              ?node ?p '"""+self.name()+"""' .   #we are looking first for the node that is the anchor of all information about the specified muscle
              ?node <http://openworm.org/entities/361> ?object .# having identified that node, here we match an object associated with the node via the 'receptor' property (number 361)
              ?object rdfs:label ?objLabel  #for the object, look up their plain text label.
            }""")

        receptors = []
        for r in qres.result:
            receptors.append(str(r[0]))

        return receptors

    def neurons(self):
        """Get neurons synapsing with this muscle

        :returns: a list of all known receptors
        :rtype: list
        """

        qres = self['semantic_net'].query(
                """SELECT ?objLabel
           WHERE {
              ?node rdfs:label '"""+self.name()+"""' .
              ?node <http://openworm.org/entities/1516> ?object .
              ?object rdfs:label ?objLabel
            }""")

        receptors = []
        for r in qres.result:
            yield str(r[0])
