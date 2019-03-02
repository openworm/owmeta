# -*- coding: utf-8 -*-
from __future__ import print_function

from .dataObject import ObjectProperty, Alias
from .connection import Connection
from .neuron import Neuron
from .biology import BiologyType
from .worm_common import WORM_RDF_TYPE


class Network(BiologyType):

    """ A network of neurons """

    class_context = BiologyType.class_context

    synapse = ObjectProperty(value_type=Connection, multiple=True)
    ''' Returns a set of all synapses in the network '''

    neuron = ObjectProperty(value_type=Neuron, multiple=True)
    ''' Returns a set of all Neuron objects in the network '''

    worm = ObjectProperty(value_rdf_type=WORM_RDF_TYPE)
    ''' The worm connected to the network '''

    synapses = Alias(synapse)
    ''' Alias to `synapse` '''

    neurons = Alias(neuron)
    ''' Alias to `neuron` '''

    def __init__(self, worm=None, **kwargs):
        super(Network, self).__init__(**kwargs)

        if worm is not None:
            self.worm(worm)

    def neuron_names(self):
        """
        Gets the complete set of neurons' names in this network.

        Example::

            # Grabs the representation of the neuronal network
            >>> net = Worm().get_neuron_network()

            #NOTE: This is a VERY slow operation right now
            >>> len(set(net.neuron_names()))
            302
            >>> set(net.neuron_names())
            set(['VB4', 'PDEL', 'HSNL', 'SIBDR', ... 'RIAL', 'MCR', 'LUAL'])

        """
        return set(x.name() for x in self.neuron())

    def aneuron(self, name):
        """
        Get a neuron by name.

        Example::

            # Grabs the representation of the neuronal network
            >>> net = Worm().get_neuron_network()

            # Grab a specific neuron
            >>> aval = net.aneuron('AVAL')

            >>> aval.type()
            set([u'interneuron'])


        :param name: Name of a c. elegans neuron
        :returns: Neuron corresponding to the name given
        :rtype: PyOpenWorm.neuron.Neuron
        """
        return Neuron.contextualize(self.context)(name=name, conf=self.conf)

    def sensory(self):
        """
        Get all sensory neurons

        :returns: A iterable of all sensory neurons
        :rtype: iter(Neuron)
        """

        n = Neuron.contextualize(self.context)()
        n.type('sensory')

        self.neuron.set(n)
        res = list(n.load())
        self.neuron.unset(n)
        return res

    def interneurons(self):
        """
        Get all interneurons

        :returns: A iterable of all interneurons
        :rtype: iter(Neuron)
        """

        n = Neuron.contextualize(self.context)()
        n.type('interneuron')

        self.neuron.set(n)
        res = list(n.load())
        self.neuron.unset(n)
        return res

    def motor(self):
        """
        Get all motor

        :returns: A iterable of all motor neurons
        :rtype: iter(Neuron)
        """

        n = Neuron.contextualize(self.context)()
        n.type('motor')

        self.neuron.set(n)
        res = list(n.load())
        self.neuron.unset(n)
        return res

    def identifier_augment(self):
        return self.make_identifier(self.worm.defined_values[0].identifier.n3())

    def defined_augment(self):
        return self.worm.has_defined_value()


__yarom_mapped_classes__ = (Network,)
