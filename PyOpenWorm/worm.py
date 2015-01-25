# -*- coding: utf-8 -*-
from .dataObject import DataObject
from .muscle import Muscle
from .cell import Cell
from .network import Network


class Worm(DataObject):
    """
    A worm.

    All worms with the same name are considered to be the same object.

    Attributes
    ----------
    neuron_network : ObjectProperty
        The neuron network of the worm
    muscle : ObjectProperty
        Muscles of the worm

    """

    def __init__(self,scientific_name=False,**kwargs):
        DataObject.__init__(self,**kwargs)
        self.name = Worm.DatatypeProperty("scientific_name", owner=self)
        Worm.ObjectProperty("neuron_network", owner=self, value_type=Network)
        Worm.ObjectProperty("muscle", owner=self, value_type=Muscle, multiple=True)
        Worm.ObjectProperty("cell", owner=self, value_type=Cell)

        if scientific_name:
            self.scientific_name(scientific_name)
        else:
            self.scientific_name("C. elegans")

    def get_neuron_network(self):
        """
        Get the network object

        :returns: An object to work with the network of the worm
        :rtype: PyOpenWorm.Network
        """
        return self.neuron_network()

    def muscles(self):
        """
        Get all muscles by name

        :returns: A set of all muscle names
        :rtype: set
         """
        return set(x.name.one() for x in self._muscles_helper())

    def _muscles_helper(self):
        for x in self.muscle.get():
            yield x

    def get_semantic_net(self):
        """
         Get the underlying semantic network as an RDFLib Graph

        :returns: A semantic network containing information about the worm
        :rtype: rdflib.ConjunctiveGraph
         """

        return self['semantic_net']

    def identifier(self, *args, **kwargs):
        # Shamelessly copy-pasted from cell.py

        # If the DataObject identifier isn't variable, then self is a specific
        # object and this identifier should be returned. Otherwise, if our name
        # attribute is _already_ set, then we can get the identifier from it and
        # return that. Otherwise, there's no telling from here what our identifier
        # should be, so the variable identifier (from DataObject.identifier() must
        # be returned
        ident = DataObject.identifier(self, *args, **kwargs)
        if 'query' in kwargs and kwargs['query'] == True:
            if not DataObject._is_variable(ident):
                return ident

            if len(self.name.v) > 0:
                # name is already set, so we can make an identifier from it
                n = self.name.one()
                return self.make_identifier(n)
            else:
                return ident
        else:
            if len(self.name.v) > 0:
                # name is already set, so we can make an identifier from it
                n = self.name.one()
                return self.make_identifier(n)
            else:
                return ident
