# -*- coding: utf-8 -*-
import PyOpenWorm as P

from PyOpenWorm.dataObject import DataObject


class Network(DataObject):

    """A network of neurons

    Attributes
    -----------
    neuron
        Representation of neurons in the network
    synapse
        Representation of synapses in the network
    """

    def __init__(self, **kwargs):
        DataObject.__init__(self, **kwargs)

        self.synapses = Network.ObjectProperty(
            'synapse',
            owner=self,
            value_type=P.Connection,
            multiple=True)
        Network.ObjectProperty(
            'neuron',
            owner=self,
            value_type=P.Neuron,
            multiple=True)
        Network.ObjectProperty(
            'worm',
            owner=self,
            value_type=P.Worm,
            multiple=False)

    def neurons(self):
        """
        Gets the complete set of neurons in this network.

        Example::

            # Grabs the representation of the neuronal network
            >>> net = P.Worm().get_neuron_network()

            #NOTE: This is a VERY slow operation right now
            >>> len(set(net.neurons()))
            302
            >>> set(net.neurons())
            set(['VB4', 'PDEL', 'HSNL', 'SIBDR', ... 'RIAL', 'MCR', 'LUAL'])

        """
        for x in self.neuron():
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
                yield P.Connection(n, nbr, int(eattr['weight']), eattr['synapse'], eattr['neurotransmitter'], conf=self.conf)

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
        ident = DataObject.identifier(self)
        if ident is None:
            if self.worm.hasValue() and self.worm.values[0].defined:
                return self.make_identifier(self.worm.values[0])
        return ident

    # def neuroml(self):
