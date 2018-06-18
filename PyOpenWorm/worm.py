# -*- coding: utf-8 -*-
from __future__ import print_function

from .dataObject import DatatypeProperty, ObjectProperty, Alias
from .muscle import Muscle
from .cell import Cell
from .biology import BiologyType
from .network import Network
from .worm_common import WORM_RDF_TYPE


class Worm(BiologyType):

    """ A representation of the whole worm """

    class_context = BiologyType.class_context

    rdf_type = WORM_RDF_TYPE

    scientific_name = DatatypeProperty()
    ''' Scientific name for the organism '''

    name = Alias(scientific_name)
    ''' Alias to `scientific_name` '''

    muscle = ObjectProperty(value_type=Muscle, multiple=True)
    ''' A type of muscle which is in the worm '''

    cell = ObjectProperty(value_type=Cell)
    ''' A cell in the worm '''

    neuron_network = ObjectProperty(value_type=Network, inverse_of=(Network, 'worm'))
    ''' The neuron network of the worm '''

    def __init__(self, scientific_name=False, **kwargs):
        super(Worm, self).__init__(**kwargs)

        if scientific_name:
            self.scientific_name(scientific_name)
        else:
            self.scientific_name("C. elegans")

    def get_neuron_network(self):
        """
        Return the neuron network of the worm.

        Example::

            # Grabs the representation of the neuronal network
            >>> net = P.Worm().get_neuron_network()

            # Grab a specific neuron
            >>> aval = net.aneuron('AVAL')

            >>> aval.type()
            set([u'interneuron'])

            #show how many connections go out of AVAL
            >>> aval.connection.count('pre')
            77

        :returns: An object to work with the network of the worm
        :rtype: PyOpenWorm.Network
        """
        return self.neuron_network()

    def muscles(self):
        """
        Get all Muscle objects attached to the Worm.

        Example::

            >>> muscles = P.Worm().muscles()
            >>> len(muscles)
            96

        :returns: A set of all muscles
        :rtype: :py:class:`set`
         """
        return set(x for x in self._muscles_helper())

    def _muscles_helper(self):
        for x in self.muscle.get():
            yield x

    def get_semantic_net(self):
        """
         Get the underlying semantic network as an RDFLib Graph

        :returns: A semantic network containing information about the worm
        :rtype: rdflib.ConjunctiveGraph
         """

        return self.rdf

    def defined_augment(self):
        ''' True if the name is defined '''
        return self.name.has_defined_value()

    def identifier_augment(self, *args, **kwargs):
        ''' Result is derived from the name property '''
        return self.make_identifier(self.name.defined_values[0])


__yarom_mapped_classes__ = (Worm,)
