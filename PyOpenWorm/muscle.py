"""
.. class:: Muscle

   muscle client
   =============

   This module contains the class that defines the muscle

"""
import PyOpenWorm as P
from PyOpenWorm import Cell

class Muscle(Cell):

    def __init__(self, name=False, **kwargs):
        Cell.__init__(self, name=name, **kwargs)
        """Get neurons synapsing with this muscle

        :returns: a list of all known receptors
        :rtype: list
        """
        P.ObjectProperty("neurons",owner=self,value_type=P.Neuron)
        P.DatatypeProperty("receptors",owner=self)

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

