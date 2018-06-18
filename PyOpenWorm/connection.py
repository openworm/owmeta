from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import six


from .biology import BiologyType
from .cell import Cell
from .dataObject import DatatypeProperty, ObjectProperty

__all__ = ['Connection']


class SynapseType:
    Chemical = 'send'
    GapJunction = 'gapJunction'


class Termination:
    Neuron = 'neuron'
    Muscle = 'muscle'


class Connection(BiologyType):

    class_context = BiologyType.class_context

    post_cell = ObjectProperty(value_type=Cell)
    ''' The post-synaptic cell '''

    pre_cell = ObjectProperty(value_type=Cell)
    ''' The pre-synaptic cell '''

    number = DatatypeProperty()
    ''' The weight of the connection '''

    synclass = DatatypeProperty()
    ''' The kind of Neurotransmitter (if any) sent between `pre_cell` and `post_cell` '''

    syntype = DatatypeProperty()
    ''' The kind of synaptic connection. 'gapJunction' indicates a gap junction and 'send' a chemical synapse '''

    termination = DatatypeProperty()
    ''' Where the connection terminates. Inferred from type of post_cell at initialization '''

    def __init__(self,
                 pre_cell=None,
                 post_cell=None,
                 number=None,
                 syntype=None,
                 synclass=None,
                 termination=None,
                 **kwargs):
        super(Connection, self).__init__(pre_cell=pre_cell,
                                         post_cell=post_cell,
                                         number=number,
                                         syntype=syntype,
                                         synclass=synclass,
                                         **kwargs)

        if isinstance(termination, six.string_types):
            termination = termination.lower()
            if termination in ('neuron', Termination.Neuron):
                self.termination(Termination.Neuron)
            elif termination in ('muscle', Termination.Muscle):
                self.termination(Termination.Muscle)

        if isinstance(syntype, six.string_types):
            syntype = syntype.lower()
            if syntype in ('send', SynapseType.Chemical):
                self.syntype(SynapseType.Chemical)
            elif syntype in ('gapjunction', SynapseType.GapJunction):
                self.syntype(SynapseType.GapJunction)

    def defined_augment(self):
        return (self.pre_cell.has_defined_value() and
                self.post_cell.has_defined_value() and
                self.syntype.has_defined_value())

    def identifier_augment(self):
        data = (self.pre_cell,
                self.post_cell,
                self.syntype)
        data = tuple(x.defined_values[0].identifier.n3() for x in data)
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
        if len(nom) == 0:
            return super(Connection, self).__str__()
        else:
            return 'Connection(' + \
                   ', '.join('{}={}'.format(n[0], n[1]) for n in nom) + \
                   ')'


__yarom_mapped_classes__ = (Connection,)
