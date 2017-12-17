# -*- coding: utf-8 -*-
from __future__ import print_function

from PyOpenWorm.dataObject import InverseProperty
from PyOpenWorm.muscle import Muscle
from PyOpenWorm.cell import Cell
from PyOpenWorm.biology import BiologyType
from PyOpenWorm.network import Network


class Worm(BiologyType):

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

    class_context = BiologyType.class_context

    def __init__(self, scientific_name=False, **kwargs):
        super(Worm, self).__init__(**kwargs)
        self.name = Worm.DatatypeProperty("scientific_name", owner=self)
        Worm.ObjectProperty(
            "muscle",
            owner=self,
            value_type=Muscle,
            multiple=True)
        Worm.ObjectProperty("cell", owner=self, value_type=Cell)
        Worm.ObjectProperty("neuron_network", owner=self, value_type=Network)

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

    @property
    def defined(self):
        return super(Worm, self).defined or self.name.has_defined_value()

    def identifier(self, *args, **kwargs):
        # If the DataObject identifier isn't variable, then self is a specific
        # object and this identifier should be returned. Otherwise, if our name
        # attribute is _already_ set, then we can get the identifier from it
        # and return that. Otherwise, there's no telling from here what our
        # identifier should be, so the variable identifier (from
        # DataObject.identifier() must be returned

        if super(Worm, self).defined:
            return super(Worm, self).identifier()
        else:
            return self.make_identifier(self.name.defined_values[0])


InverseProperty(Worm, 'neuron_network', Network, 'worm')
