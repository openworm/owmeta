import PyOpenWorm as P
from PyOpenWorm import Cell

class Muscle(Cell):
    """A single muscle cell.

    Attributes
    ----------
    neurons : ObjectProperty
        Neurons synapsing with this muscle
    receptors : DatatypeProperty
        Get a list of receptors for this muscle if called with no arguments,
        or state that this muscle has the given receptor type if called with
        an argument
    """

    def __init__(self, name=False, **kwargs):
        Cell.__init__(self, name=name, **kwargs)
        self.innervatedBy = Muscle.ObjectProperty("neurons",owner=self,value_type=P.Neuron, multiple=True)
        Muscle.DatatypeProperty("receptors",owner=self,multiple=True)

    def __str__(self):
        return self.name()
