from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals
import PyOpenWorm as P
from .dataObject import DataObject
from .cell import Cell
import six
import warnings

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
        The kind of Neurotransmitter (if any) sent between `pre_cell` and
        `post_cell`

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
            warnings.warn(
                'Passing bare strings for PyOpenWorm.Connection cells is' +
                ' deprecated. PyOpenWorm.Cell objects should be passed in' +
                ' instead.',
                DeprecationWarning)
            self.pre_cell(P.Neuron(name=pre_cell, conf=self.conf))

        if (isinstance(post_cell, P.Cell)):
            self.post_cell(post_cell)
        elif post_cell is not None:
            warnings.warn(
                'Passing bare strings for PyOpenWorm.Connection cells is' +
                ' deprecated. PyOpenWorm.Cell objects should be passed in' +
                ' instead.',
                DeprecationWarning)
            self.post_cell(P.Neuron(name=post_cell, conf=self.conf))

        if isinstance(termination, six.string_types):
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

        if isinstance(syntype, six.string_types):
            syntype = syntype.lower()
            if syntype in ('send', SynapseType.Chemical):
                self.syntype(SynapseType.Chemical)
            elif syntype in ('gapjunction', SynapseType.GapJunction):
                self.syntype(SynapseType.GapJunction)

        if isinstance(synclass, six.string_types):
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

    def __str__(self):
        nom = []
        if self.pre_cell.has_defined_value():
            nom.append(('pre_cell', self.pre_cell.values[0]))
        if self.post_cell.has_defined_value():
            nom.append(('post_cell', self.post_cell.values[0]))
        if self.syntype.has_defined_value():
            nom.append(('syntype', self.syntype.values[0]))
        if self.termination.has_defined_value():
            nom.append(('termination', self.termination.values[0]))
        if self.number.has_defined_value():
            nom.append(('number', self.number.values[0]))
        if self.synclass.has_defined_value():
            nom.append(('synclass', self.synclass.values[0]))
        return 'Connection(' + \
               ', '.join('{}={}'.format(n[0], n[1]) for n in nom) + \
               ')'
