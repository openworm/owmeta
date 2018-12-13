# -*- coding: utf-8 -*-
from __future__ import print_function

import networkx as nx

from .dataObject import ObjectProperty, Alias
from .connection import Connection
from .neuron import Neuron
from .biology import BiologyType
from .worm_common import WORM_RDF_TYPE


def _attr(obj, name, expected_len=None):
    results = list(getattr(obj, name).get())
    if expected_len is not None and len(results) != expected_len:
        raise ValueError("Attribute {} on object {} does not have length {}:\n\t{}".format(
            name, obj, expected_len, results
        ))
    return tuple(sorted(results))


def _obj_to_dict(obj, singleton_attrs=None, multi_attrs=None):
    singleton_attrs = singleton_attrs or []
    multi_attrs = multi_attrs or []

    d = dict()
    for attr_name in singleton_attrs:
        d[attr_name] = _attr(obj, attr_name, 1)[0]
    for attr_name in multi_attrs:
        d[attr_name] = _attr(obj, attr_name)

    return d


def _cell_to_dict(cell):
    cell_singletons = ["name"]
    cell_multis = ["description"]
    keys = {
        "Muscle": (cell_singletons, cell_multis + ["receptors"]),
        "Cell": (cell_singletons, cell_multis),
        "Neuron": (cell_singletons, cell_multis + ["receptors", "innexin", "neurotransmitter", "neuropeptide", "type"]),
    }

    celltype = type(cell).__name__
    singleton_attrs, multi_attrs = keys[celltype]
    d = _obj_to_dict(cell, singleton_attrs, multi_attrs)
    d["cell_type"] = celltype.lower()
    ntype = d.pop("type", None)
    if ntype is not None:
        d["neuron_type"] = ntype
    d["description"] = '\n'.join(d["description"])
    return d


def _has_unwanted_node(*cells, include_muscles, include_other):
    for cell in cells:
        type_name = type(cell).__name__
        if (not include_muscles and type_name == "Muscle") or (not include_other and type_name == "Cell"):
            return True

    return False


class Network(BiologyType):

    """ A network of neurons """

    class_context = BiologyType.class_context

    synapse = ObjectProperty(value_type=Connection, multiple=True)
    ''' Returns a set of all synapses in the network '''

    neuron = ObjectProperty(value_type=Neuron, multiple=True)
    ''' Returns a set of all Neuron objects in the network '''

    worm = ObjectProperty(value_rdf_type=WORM_RDF_TYPE)

    synapses = Alias(synapse)
    neurons = Alias(neuron)

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

    def as_networkx(self, include_muscles=True, include_other=True):
        """
        Return the network as a networkx OrderedMultiDiGraph.
        It is ordered for determinism/repeatability,
        a multigraph because chemical synapses and gap junctions can be in parallel,
        and directed because chemical synapses have a direction (and gap junctions may be rectifying).

        Nodes are the string names of the cells, and have data associated with them:
        - All nodes have data ``name: str, description: str, cell_type: str``
        - Neurons additionally have ``receptors: Tuple[str], innexin: Tuple[str], neurotransmitter: Tuple[str], neuropeptide: Tuple[str], neuron_type: Tuple[str]``
        - Muscles additionally have ``receptors: Tuple[str]``

        Tuples of strings are sorted lexicographically.
        ``cell_type`` is any of ``"Neuron", "Muscle", "Cell"``.
        ``neuron_type`` is any combination of ``"interneuron", "sensory", "motor"``

        Edges also have data: ``syntype: str, number: int, termination: str``

        ``syntype`` is any of ``"send", "gapJunction"``.
        ``termination`` is any of ``"", "muscle", "neuron"``

        :param include_muscles: Whether to include muscle cells
        :param include_other: Whether to include cells which are neither muscles nor neurons
        :return: nx.OrderedMultiDiGraph
        """
        connection_dicts = []
        cell_dicts = dict()

        for connection in self.synapse.get():
            d = _obj_to_dict(connection, ["syntype", "number"], ["termination"])

            attr_names = ("pre_cell", "post_cell")

            cells = [_attr(connection, name, 1)[0] for name in attr_names]
            if _has_unwanted_node(*cells, include_muscles=include_muscles, include_other=include_other):
                continue

            for cell, name in zip(cells, attr_names):
                if cell not in cell_dicts:
                    cell_dicts[cell] = _cell_to_dict(cell)
                cell_dict = cell_dicts[cell]
                d[name] = cell_dict["name"]

            d["termination"] = d["termination"][0] if d["termination"] else ''

            connection_dicts.append(d)

        g = nx.OrderedMultiDiGraph()
        g.graph["include_muscles"] = include_muscles
        g.graph["include_other"] = include_other

        for n in sorted(cell_dicts.values(), key=lambda d: d["name"]):
            g.add_node(n["name"], **n)

        for c in sorted(connection_dicts, key=lambda d: (d["pre_cell"], d["post_cell"], d["syntype"])):
            g.add_edge(c["pre_cell"], c["post_cell"], **c)

        return g

    def identifier_augment(self):
        return self.make_identifier(self.worm.defined_values[0].identifier.n3())

    def defined_augment(self):
        return self.worm.has_defined_value()


__yarom_mapped_classes__ = (Network,)
