from __future__ import print_function

from wrapt import ObjectProxy
from .pProperty import Property
from .dataObject import DatatypeProperty, Alias
from .cell import Cell
from .connection import Connection


class NeuronProxy(ObjectProxy):

    def __init__(self, neighbor, connection, *args):
        super(NeuronProxy, self).__init__(*args)
        self._self_neighbor = neighbor
        self._self_connection = connection

    @property
    def neighbor(self):
        return self._self_neighbor

    @property
    def connection(self):
        return self._self_connection


class Neuron(Cell):

    """
    A neuron.

    See what neurons express some neuropeptide

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

        >>> aval.name()
        u'AVAL'

        #list all known receptors
        >>> sorted(aval.receptors())
        [u'GGR-3', u'GLR-1', u'GLR-2', u'GLR-4', u'GLR-5', u'NMR-1', u'NMR-2', u'UNC-8']

        #show how many chemical synapses go in and out of AVAL
        >>> aval.Syn_degree()
        90

    Parameters
    ----------
    name : string
        The name of the neuron.

    Attributes
    ----------
    neighbor : Property
        Get neurons connected to this neuron if called with no arguments, or
        with arguments, state that neuronName is a neighbor of this Neuron
    connection : Property
        Get a set of Connection objects describing chemical synapses or gap
        junctions between this neuron and others

    """

    class_context = Cell.class_context

    type = DatatypeProperty(multiple=True)
    ''' The neuron type (i.e., sensory, interneuron, motor) '''

    receptor = DatatypeProperty(multiple=True)
    ''' The receptor types associated with this neuron '''

    innexin = DatatypeProperty(multiple=True)
    ''' Innexin types associated with this neuron '''

    neurotransmitter = DatatypeProperty(multiple=True)
    ''' Neurotransmitters associated with this neuron '''

    neuropeptide = DatatypeProperty(multiple=True)
    ''' Name of the gene corresponding to the neuropeptide produced by this neuron '''

    receptors = Alias(receptor)
    ''' Alias to py:attr:`receptor` '''

    def __init__(self, name=False, **kwargs):
        super(Neuron, self).__init__(name=name, **kwargs)
        # Get neurons connected to this neuron
        Neighbor(owner=self)
        # Get connections from this neuron
        ConnectionProperty(owner=self)

        self.get_neighbors = self.neighbor

    def contextualize(self, context):
        res = super(Neuron, self).contextualize(context)
        if hasattr(self, 'neighbor'):
            res = NeuronProxy(self.neighbor.contextualize(context),
                              self.connection.contextualize(context),
                              res)
        return res

    def GJ_degree(self):
        """Get the degree of this neuron for gap junction edges only

        :returns: total number of incoming and outgoing gap junctions
        :rtype: int
        """
        count = 0
        for c in self.connection():
            if c.syntype.one() == 'gapJunction':
                count += 1
        return count

    def Syn_degree(self):
        """Get the degree of this neuron for chemical synapse edges only

        :returns: total number of incoming and outgoing chemical synapses
        :rtype: int
        """
        count = 0
        for c in self.connection.get('either'):
            if c.syntype.one() == 'send':
                count += 1
        return count

    def get_incidents(self, type=0):
        """ Get neurons which synapse at this neuron """
        # Directed graph. Getting accessible _from_ this node
        for item in self['nx'].in_edges_iter(self.name(), data=True):
            if 'GapJunction' in item[2]['synapse']:
                yield item[0]

    def _as_neuroml(self):
        """Return this neuron as a NeuroML representation

           :rtype: libNeuroML.Neuron
        """


class Neighbor(Property):
    multiple = True

    def __init__(self, **kwargs):
        super(Neighbor, self).__init__('neighbor', **kwargs)
        self._conns = []
        self._conntype = Connection.contextualize(self.owner.context)
        self.context = self.owner.context

    def contextualize(self, context):
        res = type(self)(owner=self.owner)
        res._conns = self._conns
        res._conntype = Connection.contextualize(context)
        res.context = context
        return res

    def get(self, **kwargs):
        """Get a list of neighboring neurons.

           Parameters
           ----------
           See parameters for PyOpenWorm.connection.Connection

           Returns
           -------
           list of Neuron
        """
        if len(self._conns) > 0:
            for c in self._conns:
                if c.context == self.context:
                    for post in c.post_cell.get():
                        yield post
        else:
            conn = self._conntype.contextualize(self.context)(pre_cell=self.owner, **kwargs)
            for r in conn.post_cell.get():
                yield r

    def count(self, **kwargs):
        conntype = self._conntype.contextualize(self.context)
        return conntype(pre_cell=self.owner, **kwargs).count()

    @property
    def defined_values(self):
        return []

    @property
    def values(self):
        return []

    def set(self, other, **kwargs):
        c = self._conntype(pre_cell=self.owner, post_cell=other, **kwargs)
        self._conns.append(c)
        return c

    def triples(self, **kwargs):
        for c in self._conns:
            for x in c.triples(**kwargs):
                yield x


class ConnectionProperty(Property):

    """A representation of the connection between neurons. Either a gap junction
    or a chemical synapse

    TODO: Add neurotransmitter type.
    TODO: Add connection strength
    """

    multiple = True

    def __init__(self, **kwargs):
        super(ConnectionProperty, self).__init__('connection', **kwargs)
        self._conns = []
        self._conntype = Connection.contextualize(self.owner.context)

    def get(self, pre_post_or_either='pre', **kwargs):
        """Get a list of connections associated with the owning neuron.

           Parameters
           ----------
           pre_post_or_either: str
               What kind of connection to look for.
               'pre': Owner is the source of the connection
               'post': Owner is the destination of the connection
               'either': Owner is either the source or destination of the connection

           Returns
           -------
           list of Connection
        """
        c = []
        ct = self._conntype.contextualize(self.context)
        if pre_post_or_either == 'pre':
            c.append(ct(pre_cell=self.owner, **kwargs))
        elif pre_post_or_either == 'post':
            c.append(ct(post_cell=self.owner, **kwargs))
        elif pre_post_or_either == 'either':
            c.append(ct(pre_cell=self.owner, **kwargs))
            c.append(ct(post_cell=self.owner, **kwargs))

        for x in c:
            for r in x.load():
                yield r

        for x in self._conns:
            if x.defined and x.context == self.context:
                yield x

    def contextualize(self, context):
        res = type(self)(owner=self.owner)
        res._conns = self._conns
        res.context = context
        return res

    @property
    def values(self):
        return []

    def count(self, pre_post_or_either='pre', *args, **kwargs):
        res = 0
        conntype = self._conntype.contextualize(self.context)
        if pre_post_or_either == 'pre':
            res += conntype(pre_cell=self.owner, **kwargs).count()
        elif pre_post_or_either == 'post':
            res += conntype(post_cell=self.owner, **kwargs).count()
        elif pre_post_or_either == 'either':
            res += conntype(pre_cell=self.owner, **kwargs).count() + \
                    conntype(post_cell=self.owner, **kwargs).count()

        return res

    def set(self, conn, **kwargs):
        """Add a connection associated with the owner Neuron

           Parameters
           ----------
           conn : PyOpenWorm.connection.Connection
               connection associated with the owner neuron

           Returns
           -------
           A PyOpenWorm.neuron.Connection
        """
        assert(isinstance(conn, self._conntype))
        self._conns.append(conn)

    def triples(self, **kwargs):
        for c in self._conns:
            for x in c.triples(**kwargs):
                yield x


__yarom_mapped_classes__ = (Neuron,)
