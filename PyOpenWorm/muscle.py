import PyOpenWorm as P
from PyOpenWorm import Cell

class Muscle(Cell):
    """A single muscle cell

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
