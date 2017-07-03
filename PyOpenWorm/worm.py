# -*- coding: utf-8 -*-
from __future__ import print_function
from .dataObject import DataObject
from .muscle import Muscle
from .cell import Cell
from .network import Network
from .simpleProperty import ObjectProperty


class NeuronNetworkProperty(ObjectProperty):
    value_type = Network
    linkName = 'neuron_network'
    multiple = False
    property_type = 'ObjectProperty'

    def __init__(self, **kwargs):
        super(NeuronNetworkProperty, self).__init__(**kwargs)
        self.link = self.owner.rdf_namespace[self.linkName]

    def set(self, v):
        super(NeuronNetworkProperty, self).set(v)
        if isinstance(v, Network) and isinstance(self.owner, Worm):
            v.worm(self.owner)

    @property
    def value_rdf_type(self):
        return Network.rdf_type


class Worm(DataObject):

    """
    A representation of the whole worm.

    All worms with the same name are considered to be the same object.

    Attributes
    ----------
    neuron_network : ObjectProperty
        The neuron network of the worm
    muscle : ObjectProperty
        Muscles of the worm

    """

    def __init__(self, scientific_name=False, **kwargs):
        super(Worm, self).__init__(**kwargs)
        self.name = Worm.DatatypeProperty("scientific_name", owner=self)
        Worm.ObjectProperty(
            "muscle",
            owner=self,
            value_type=Muscle,
            multiple=True)
        Worm.ObjectProperty("cell", owner=self, value_type=Cell)
        self.attach_property(self, NeuronNetworkProperty)

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
        :rtype: set
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

    def defined(self):
        return super(Worm,self).defined or self.name.has_defined_value()

    def identifier(self, *args, **kwargs):
        # If the DataObject identifier isn't variable, then self is a specific
        # object and this identifier should be returned. Otherwise, if our name
        # attribute is _already_ set, then we can get the identifier from it and
        # return that. Otherwise, there's no telling from here what our identifier
        # should be, so the variable identifier (from DataObject.identifier() must
        # be returned

        if super(Worm, self).defined:
            return super(Worm,self).identifier()
        else:
            return self.make_identifier(self.name.defined_values[0])
