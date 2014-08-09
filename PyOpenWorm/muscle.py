"""
.. class:: Muscle

   muscle client
   =============

   This module contains the class that defines the muscle

"""
import PyOpenWorm as P
from PyOpenWorm import Cell

class Muscle(Cell):

    """
    Attributes
    ----------
    neurons : ObjectProperty
        Neurons synapsing with this muscle
    """
    objectProperties = [("neurons", P.Neuron)]
    datatypeProperties = ["receptors"]
    def __init__(self, name=False, **kwargs):
        Cell.__init__(self, name=name, **kwargs)
        self.innervatedBy = self.neurons
