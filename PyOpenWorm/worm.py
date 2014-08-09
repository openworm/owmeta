# -*- coding: utf-8 -*-
"""
.. class:: Worm

   This module contains the class that defines the worm as a whole

"""

import PyOpenWorm as P
from PyOpenWorm import DataObject


class Worm(DataObject):
    """
    A worm

    All worms with the same name are considered to be the same object.

    Attributes
    ----------
    neuron_network : ObjectProperty
        The neuron network of the worm
    muscle : ObjectProperty
        Muscles of the worm

    """
    objectProperties = [('neuron_network','Network'),
                        ('muscle','Muscle'),
                        ('cell', 'Cell')]
    datatypeProperties = ['scientific_name']
    def __init__(self,scientific_name=False,**kwargs):
        DataObject.__init__(self,**kwargs)

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
        for x in self.neuron_network():
            return x

    def muscles(self):
        """
        Get all muscles by name

        :returns: A list of all muscle names
        :rtype: list
         """
        for x in self.muscle():
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
                n = next(self.name())
                return self.make_identifier(n)
            else:
                return ident
        else:
            if len(self.name.v) > 0:
                # name is already set, so we can make an identifier from it
                n = next(self.name())
                return self.make_identifier(n)
            else:
                return ident
