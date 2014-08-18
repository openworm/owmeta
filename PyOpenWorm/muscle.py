import PyOpenWorm as P
from PyOpenWorm import Cell

class Muscle(Cell):
    """A single muscle cell

    Attributes
    ----------
    neurons : ObjectProperty
        Neurons synapsing with this muscle
    """

    def __init__(self, name=False, **kwargs):
        Cell.__init__(self, name=name, **kwargs)
        self.innervatedBy = Muscle.ObjectProperty("neurons",owner=self,value_type=P.Neuron)
        Muscle.DatatypeProperty("receptors",owner=self)
