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

    key_properties = (pre_cell, post_cell, syntype)

    # Arguments are given explicitly here to support positional arguments
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

    def __str__(self):
        nom = []
        props = ('pre_cell', 'post_cell', 'syntype', 'termination', 'number', 'synclass',)
        for p in props:
            if getattr(self, p).has_defined_value():
                nom.append((p, getattr(self, p).defined_values[0]))
        if len(nom) == 0:
            return super(Connection, self).__str__()
        else:
            return 'Connection(' + \
                   ', '.join('{}={}'.format(n[0], n[1]) for n in nom) + \
                   ')'


__yarom_mapped_classes__ = (Connection,)
