# -*- coding: utf-8 -*-
from __future__ import print_function
import PyOpenWorm as P

from PyOpenWorm.dataObject import DataObject


class Network(DataObject):

    """A network of neurons

    Attributes
    -----------
    neuron
        Returns a set of all Neuron objects in the network
    synapse
        Returns a set of all synapses in the network
    """

    def __init__(self, **kwargs):
        super(Network, self).__init__(**kwargs)
        self.synapses = Network.ObjectProperty(
            'synapse',
            owner=self,
            value_type=P.Connection,
            multiple=True)
        self.neurons = Network.ObjectProperty(
            'neuron',
            owner=self,
            value_type=P.Neuron,
            multiple=True)
        Network.ObjectProperty(
            'worm',
            owner=self,
            value_type=P.Worm,
            multiple=False)

    def neuron_names(self):
        """
        Gets the complete set of neurons' names in this network.

        Example::

            # Grabs the representation of the neuronal network
            >>> net = P.Worm().get_neuron_network()

            #NOTE: This is a VERY slow operation right now
            >>> len(set(net.neuron_names()))
            302
            >>> set(net.neuron_names())
            set(['VB4', 'PDEL', 'HSNL', 'SIBDR', ... 'RIAL', 'MCR', 'LUAL'])

        """
        for x in self.neurons():
            yield x.name()

    def aneuron(self, name):
        """
        Get a neuron by name.

        Example::

            # Grabs the representation of the neuronal network
            >>> net = P.Worm().get_neuron_network()

            # Grab a specific neuron
            >>> aval = net.aneuron('AVAL')

            >>> aval.type()
            set([u'interneuron'])


        :param name: Name of a c. elegans neuron
        :returns: Neuron corresponding to the name given
        :rtype: PyOpenWorm.Neuron
        """
        n = P.Neuron(name=name, conf=self.conf)
        return n

    def _synapses_csv(self):
        """
        Get all synapses into CSV

        :returns: A generator of Connection objects
        :rtype: generator
        """
        for n, nbrs in self['nx'].adjacency_iter():
            for nbr, eattr in nbrs.items():
                yield P.Connection(n,
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

        # TODO: make sure these belong to *this* Network
        n = P.Neuron()
        n.type('sensory')

        for x in n.load():
            yield x

    def interneurons(self):
        """
        Get all interneurons

        :returns: A iterable of all interneurons
        :rtype: iter(Neuron)
        """

        # TODO: make sure these belong to *this* Network
        n = P.Neuron()
        n.type('interneuron')

        for x in n.load():
            yield x

    def motor(self):
        """
        Get all motor

        :returns: A iterable of all motor neurons
        :rtype: iter(Neuron)
        """

        # TODO: make sure these belong to *this* Network
        n = P.Neuron()
        n.type('motor')

        for x in n.load():
            yield x

    def identifier(self, *args, **kwargs):
        if super(Network, self).defined:
            return super(Network, self).identifier()
        else:
            return self.make_identifier(self.worm.defined_values[0])

    @property
    def defined(self):
        return super(Network, self).defined or self.worm.has_defined_value()

    # def neuroml(self):
