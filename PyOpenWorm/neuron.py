import sqlite3
import sys
import PyOpenWorm as P
from PyOpenWorm import Cell


# XXX: Should we specify somewhere whether we have NetworkX or something else?

class Neighbor(P.Property):
    def __init__(self,**kwargs):
        P.Property.__init__(self,'neighbor',**kwargs)
        self._conns = []

    def get(self,**kwargs):
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
                for x in c.post_cell():
                    yield x
        else:
            c = P.Connection(pre_cell=self.owner,**kwargs)
            for r in c.load():
                for x in r.post_cell():
                    yield x

    def set(self, other, **kwargs):
        c = P.Connection(pre_cell=self.owner,post_cell=other,**kwargs)
        self._conns.append(c)
        return c

    def triples(self,**kwargs):
        for c in self._conns:
            for x in c.triples(**kwargs):
                yield x

class Connection(P.Property):
    def __init__(self,**kwargs):
        P.Property.__init__(self,'connection',**kwargs)
        self._conns = []

    def get(self,pre_post_or_either='pre',**kwargs):
        """Get a list of connections associated with the owning neuron.

           Parameters
           ----------
           type: What kind of junction to look for.
                        0=all, 1=gap junctions only, 2=all chemical synapses
                        3=incoming chemical synapses, 4=outgoing chemical synapses
           Returns
           -------
           list of Connection
        """
        c = []
        if pre_post_or_either == 'pre':
            c.append(P.Connection(pre_cell=self.owner,**kwargs))
        elif pre_post_or_either == 'post':
            c.append(P.Connection(post_cell=self.owner,**kwargs))
        elif pre_post_or_either == 'either':
            c.append(P.Connection(pre_cell=self.owner,**kwargs))
            c.append(P.Connection(post_cell=self.owner,**kwargs))
        for x in c:
            for r in x.load():
                yield r
    def count(self,pre_post_or_either='pre',syntype=None, *args,**kwargs):
        """Get a list of connections associated with the owning neuron.

           Parameters
           ----------
           See parameters for PyOpenWorm.connection.Connection

           Returns
           -------
           int
               The number of connections matching the paramters given
        """
        # XXX: Turn this into a COUNT query
        options = dict()
        options["pre"] = """
                     ?x c:pre_cell ?z .
                     ?z sp:value <%s> .
                     """ % self.owner.identifier()
        options["post"] = """
                      ?x c:post_cell ?z .
                      ?z sp:value <%s> .
                      """ % self.owner.identifier()
        options["either"] = " { %s } UNION { %s } . " % (options['post'], options['pre'])

        if syntype is not None:
            if syntype.lower() == 'gapjunction':
                syntype='gapJunction'
            syntype_pattern = "FILTER( EXISTS { ?x c:syntype ?v . ?v sp:value \"%s\" . }) ." % syntype
        else:
            syntype_pattern = ''

        q = """
        prefix ow: <http://openworm.org/entities/>
        prefix c: <http://openworm.org/entities/Connection/>
        prefix sp: <http://openworm.org/entities/SimpleProperty/>
        prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT (COUNT(?x) as ?count) WHERE {
         %s
         %s
        }
        """ % (options[pre_post_or_either], syntype_pattern)

        res = 0
        for x in self.conf['rdf.graph'].query(q):
            res = x['count']
        return int(res)

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
        #XXX: Should this create a Connection here instead?
        assert(isinstance(conn, P.Connection))
        self._conns.append(conn)

    def triples(self,**kwargs):
        for c in self._conns:
            for x in c.triples(**kwargs):
                yield x

class Neuron(Cell):
    """
    A neuron.

    Parameters
    ----------
    name : string
        The name of the neuron.

    Attributes
    ----------
    type : DatatypeProperty
        The neuron type (i.e., sensory, interneuron, motor)
    receptor : DatatypeProperty
        The receptor types associated with this neuron
    innexin : DatatypeProperty
        Innexin types associated with this neuron
    neighbor : Property
        Get neurons connected to this neuron
    connection : Property
        Get connections associated with this neuron
    """
    datatypeProperties = ["type",
                          "receptor",
                          "innexin",]
    def __init__(self, name=False, **kwargs):
        Cell.__init__(self,name=name,**kwargs)
        # Get neurons connected to this neuron
        Neighbor(owner=self)
        # Get connections from this neuron
        Connection(owner=self)

        ### Aliases ###
        self.get_neighbors = self.neighbor
        self.receptors = self.receptor

    def GJ_degree(self):
        """Get the degree of this neuron for gap junction edges only

        :returns: total number of incoming and outgoing gap junctions
        :rtype: int
        """

        count = 0
        for item in self['nx'].in_edges_iter(self.name(),data=True):
            if 'GapJunction' in item[2]['synapse']:
                count = count + 1
        for item in self['nx'].out_edges_iter(self.name(),data=True):
            if 'GapJunction' in item[2]['synapse']:
                count = count + 1
        return count

    def Syn_degree(self):
        """Get the degree of a this neuron for chemical synapse edges only

        :returns: total number of incoming and outgoing chemical synapses
        :rtype: int
        """
        count = 0
        for item in self['nx'].in_edges_iter(self.name(),data=True):
            if 'Send' in item[2]['synapse']:
                count = count + 1
        for item in self['nx'].out_edges_iter(self.name(),data=True):
            if 'Send' in item[2]['synapse']:
                count = count + 1
        return count

    def _type_semantic(self):
        """Get type of this neuron (motor, interneuron, sensory)

        Use the semantic database as the source

        :returns: the type
        :rtype: str
        """

        qres = self['rdf.graph'].query(
          """SELECT ?objLabel     #we want to get out the labels associated with the objects
           WHERE {
              ?node ?p '"""+self.name()+"""' .   #we are looking first for the node that is the anchor of all information about the specified neuron
              ?node <http://openworm.org/entities/1515> ?object .# having identified that node, here we match an object associated with the node via the 'is a' property (number 1515)
              ?object rdfs:label ?objLabel  #for the object, look up their plain text label.
            }""")

        type = ''
        for r in qres.result:
            type = str(r[0])

        return type

    def _type_networkX(self):
        """Get type of this neuron (motor, interneuron, sensory)

        Use the networkX representation as the source

        :returns: the type
        :rtype: str
        """
        return self['nx'].node[self.name.one()]['ntype']


    def get_incidents(self, type=0):
        """ Get neurons which synapse at this neuron """
        # Directed graph. Getting accessible _from_ this node
        for item in self['nx'].in_edges_iter(self.name(),data=True):
            if 'GapJunction' in item[2]['synapse']:
                yield item[0]

    def _as_neuroml(self):
       """Return this neuron as a NeuroML representation

          :rtype: libNeuroML.Neuron
       """


