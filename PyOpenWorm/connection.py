from __future__ import print_function
import PyOpenWorm as P
from .dataObject import DataObject
from .cell import Cell

__all__ = ['Connection']


class SynapseType:
    Chemical = 'send'
    GapJunction = 'gapJunction'


class Termination:
    Neuron = 'neuron'
    Muscle = 'muscle'


class Connection(DataObject):

    """Connection between Cells

    Parameters
    ----------
    pre_cell : string, Muscle or Neuron, optional
        The pre-synaptic cell
    post_cell : string, Muscle or Neuron, optional
        The post-synaptic cell
    number : int, optional
        The weight of the connection
    syntype : {'gapJunction', 'send'}, optional
        The kind of synaptic connection. 'gapJunction' indicates
        a gap junction and 'send' a chemical synapse
    synclass : string, optional
        The kind of Neurotransmitter (if any) sent between `pre_cell` and `post_cell`

    Attributes
    ----------
    termination : {'neuron', 'muscle'}
        Where the connection terminates. Inferred from type of post_cell
    """

    def __init__(self,
                 pre_cell=None,
                 post_cell=None,
                 number=None,
                 syntype=None,
                 synclass=None,
                 termination=None,
                 **kwargs):
        super(Connection, self).__init__(**kwargs)

        Connection.ObjectProperty('post_cell', owner=self, value_type=Cell)
        Connection.ObjectProperty('pre_cell', owner=self, value_type=Cell)

        Connection.DatatypeProperty('number', owner=self)
        Connection.DatatypeProperty('synclass', owner=self)
        Connection.DatatypeProperty('syntype', owner=self)
        Connection.DatatypeProperty('termination', owner=self)

        if isinstance(pre_cell, P.Cell):
            self.pre_cell(pre_cell)
        elif pre_cell is not None:
            # TODO: don't assume that the pre_cell is a neuron
            self.pre_cell(P.Neuron(name=pre_cell, conf=self.conf))

        if (isinstance(post_cell, P.Cell)):
            self.post_cell(post_cell)
        elif post_cell is not None:
            # TODO: don't assume that the post_cell is a neuron
            self.post_cell(P.Neuron(name=post_cell, conf=self.conf))

        if isinstance(termination, basestring):
            termination = termination.lower()
            if termination in ('neuron', Termination.Neuron):
                self.termination(Termination.Neuron)
            elif termination in ('muscle', Termination.Muscle):
                self.termination(Termination.Muscle)

        if isinstance(number, int):
            self.number(int(number))
        elif number is not None:
            raise Exception(
                "Connection number must be an int, given %s" %
                number)

        if isinstance(syntype, basestring):
            syntype = syntype.lower()
            if syntype in ('send', SynapseType.Chemical):
                self.syntype(SynapseType.Chemical)
            elif syntype in ('gapjunction', SynapseType.GapJunction):
                self.syntype(SynapseType.GapJunction)

        if isinstance(synclass, basestring):
            self.synclass(synclass)

    @property
    def defined(self):
        return super(Connection, self).defined or \
            (self.pre_cell.has_defined_value()
             and self.post_cell.has_defined_value()
             and self.syntype.has_defined_value())

    def identifier(self, *args, **kwargs):
        if super(Connection, self).defined:
            return super(Connection, self).identifier()
        else:
            data = (self.pre_cell,
                    self.post_cell,
                    self.syntype)
            data = tuple(x.defined_values[0].identifier().n3() for x in data)
            data = "".join(data)
            return self.make_identifier(data)
