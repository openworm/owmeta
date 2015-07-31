import PyOpenWorm as P
from PyOpenWorm import Cell

class Muscle(Cell):
    """A single muscle cell.

    See what neurons innervate a muscle:

    Example::

        >>> mdr21 = P.Muscle('MDR21')
        >>> innervates_mdr21 = mdr21.innervatedBy()
        >>> len(innervates_mdr21)
        4

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
        super(Muscle,self).__init__(name=name, **kwargs)
        self.innervatedBy = Muscle.ObjectProperty("neurons",owner=self,value_type=P.Neuron, multiple=True)
        Muscle.DatatypeProperty("receptors",owner=self,multiple=True)

