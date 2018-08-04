from rdflib.term import URIRef
from .dataObject import DataObject, DatatypeProperty, UnionProperty, Alias


class Bag(DataObject):

    """
    A convenience class for working with a collection of objects

    Example::

        v = Bag('unc-13 neurons and muscles')
        n = P.Neuron()
        m = P.Muscle()
        n.receptor('UNC-13')
        m.receptor('UNC-13')
        for x in n.load():
            v.value(x)
        for x in m.load():
            v.value(x)
        # Save the group for later use
        v.save()
        ...
        # get the list back
        u = Bag('unc-13 neurons and muscles')
        nm = list(u.value())


    Parameters
    ----------
    group_name : string
        A name of the group of objects

    Attributes
    ----------
    name : DatatypeProperty
        The name of the group of objects
    value : ObjectProperty
        An object in the group
    add : ObjectProperty
        an alias for ``value``

    """

    class_context = URIRef('http://openworm.org/schema')
    value = UnionProperty()
    add = Alias(value)
    name = DatatypeProperty()
    group_name = Alias(name)

    def defined_augment(self):
        return self.group_name.has_defined_value()

    def identifier_augment(self):
        return self.make_identifier(self.group_name)


__yarom_mapped_classes__ = (Bag,)
