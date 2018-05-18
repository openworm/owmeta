# -*- coding: utf-8 -*-
from __future__ import print_function

from PyOpenWorm.connection import Connection
from PyOpenWorm.neuron import Neuron
from PyOpenWorm.biology import BiologyType


class Network(BiologyType):

    """A network of neurons

    Attributes
    -----------
    neuron
        Returns a set of all Neuron objects in the network
    synapse
        Returns a set of all synapses in the network
    """

    class_context = BiologyType.class_context

    def __init__(self, worm=None, **kwargs):
        super(Network, self).__init__(**kwargs)
        self.synapses = Network.ObjectProperty(
            'synapse',
            owner=self,
            value_type=Connection,
            multiple=True)
        self.neurons = Network.ObjectProperty(
            'neuron',
            owner=self,
            value_type=Neuron,
            multiple=True)
        from PyOpenWorm.worm import Worm
        Network.ObjectProperty(
            'worm',
            owner=self,
            value_type=Worm,
            multiple=False)

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

    def _synapses_csv(self):
        """
        Get all synapses into CSV

        :returns: A generator of Connection objects
        :rtype: generator
        """
        for n, nbrs in self['nx'].adjacency_iter():
            for nbr, eattr in nbrs.items():
                yield Connection(n,
                                 nbr,
                                 int(eattr['weight']),
                                 eattr['synapse'],
                                 eattr['neurotransmitter'],
                                 conf=self.conf)

    def as_networkx(self):
        return self['nx']

    def sensory(self):
        """
        Get all sensory neurons

        :returns: A iterable of all sensory neurons
        :rtype: iter(Neuron)
        """

        n = Neuron()
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

        n = Neuron()
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

        n = Neuron()
        n.type('motor')

        self.neuron.set(n)
        res = list(n.load())
        self.neuron.unset(n)
        return res

    def identifier_augment(self):
        return self.make_identifier(self.worm.defined_values[0].identifier.n3())

    def defined_augment(self):
        return self.worm.has_defined_value()

    # def neuroml(self):


__yarom_mapped_classes__ = (Network,)
