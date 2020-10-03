from owmeta_core.dataobject import DatatypeProperty, ObjectProperty, Alias

from .cell import Cell
from .neuron import Neuron


class Muscle(Cell):
    """
    A single muscle cell.

    See what neurons innervate a muscle:

    Example::

        >>> mdr21 = Muscle('MDR21')
        >>> innervates_mdr21 = mdr21.innervatedBy()
        >>> len(innervates_mdr21)
        4
    """

    class_context = Cell.class_context

    innervatedBy = ObjectProperty(value_type=Neuron, multiple=True)
    ''' Neurons synapsing with this muscle '''

    neurons = Alias(innervatedBy)
    ''' Alias to `innervatedBy` '''

    receptors = DatatypeProperty(multiple=True)
    ''' Receptor types expressed by this type of muscle '''

    receptor = Alias(receptors)
    ''' Alias to `receptors` '''


class BodyWallMuscle(Muscle):
    '''
    A somatic muscle cell that lies close under the skin and basal lamina of C. elegans
    and allows the worm to move
    '''
    class_context = Cell.class_context
