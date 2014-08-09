"""
.. class:: Neuron

   neuron client
   =============

   This module contains the class that defines the neuron

"""

import sqlite3
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
    def count(self,*args,**kwargs):
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
        return len(list(self.get(*args,**kwargs)))

    def set(self, conn, **kwargs):
        """Add a connection associated with the owner Neuron

           Parameters
           ----------
           type: What kind of junction to look for.
                        0=all, 1=gap junctions only, 2=all chemical synapses
                        3=incoming chemical synapses, 4=outgoing chemical synapses
           Returns
           -------
           list of Connection
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

    def _write_out_db(self):
        con = sqlite3.connect(self['sqldb'])
        with open(self['sqldb'], 'w') as f:
            for line in con.iterdump():
                f.write('%s\n' % line)

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
        return self['nx'].node[self.name()]['ntype']

    #def add_reference(self, type, item, pmid = None, doi = None, wormbaseid = None):
        #"""Add a reference that provides evidence of the relationship between
            #this neuron and one of its elements.

            #Example::

                #>>>aval = PyOpenWorm.Neuron('AVAL')
               #>>>aval.receptors()
               #['GLR-1', 'NMR-1', 'GLR-4', 'GLR-2', 'GGR-3', 'UNC-8', 'GLR-5', 'NMR-2']
               ##look up what reference says this neuron has a receptor GLR-1
               #>>>aval.get_reference(0,'GLR-1')
               #None
                   #>>>aval.add_reference(0,'GLR-1', doi='125.41.3/ploscompbiol',
                           #pmid = '57182010')
                   #>>>aval.get_reference(0,'GLR-1')
                   #['http://dx.doi.org/125.41.3/ploscompbiol', 'http://pubmedcentral.nih.gov/57182010']
        #:param type: The kind of thing to add.  Valid options are: 0=receptor, 1=neighbor
        #:param item: Name of the item
            #:param doi: A Digital Object Identifier (DOI) that provides evidence, optional
            #:param pmid: A PubMed ID (PMID) that point to a paper that provides evidence, optional
            #:param wormbaseid: An ID from WormBase that points to a record that provides evidence, optional
        #"""

        #try:
            #t = propertyTypes[type]
        #except KeyError:
            ## XXX: need logging
            #print 'not a valid type ' + type
            #return

        #qres = self['rdf.graph'].query(
          #"""SELECT ?this ?p ?that
           #WHERE {
              #?this rdfs:label '"""+self.name()+"""' .
              #?that rdfs:label '"""+item +"""' .
              #?this <"""+t+"""> ?that .
              #bind (<"""+t+"""> as ?p)
            #}""")
        #if len(qres) > 0:
            ##XXX: Should verify that we're given a valid uri
            #ui = self['molecule_name'](pmid)
            #DataUser.add_reference(self, [qres], ui)

    #def get_reference(self, type, item=''):
        #"""Get a reference back that provides the evidence that this neuron is
           #associated with the item requested as a list of URLs.

           #Example::

               #>>>ader = PyOpenWorm.Neuron('ADER')
               #>>>ader.receptors()
             #['ACR-16', 'TYRA-3', 'DOP-2', 'EXP-1']
               ##look up what reference says this neuron has a receptor EXP-1
               #>>>ader.get_reference(0,'EXP-1')
               #['http://dx.doi.org/10.100.123/natneuro']
               ##look up what reference says this neuron has a neighbor DD5
               #>>>ader.get_reference(1, 'DD5')
               #['http://dx.doi.org/20.140.521/ploscompbiol']

           #:param type: The kind of thing to search for.  Valid options are: 0=receptor, 1=neighbor
           #:param item: Name of the item requested, if appropriate
           #:returns: a list of URLs that points to references
           #:rtype: list
        #"""
        #try:
            #t = propertyTypes[type]
        #except KeyError:
            ## XXX: need logging
            #print 'not a valid type ' + str(type)
            #return

        #qres = self['rdf.graph'].query(
            #"""
            #SELECT ?prov #we want to get out the labels associated with the objects
            #WHERE {
                    #?node rdfs:label '"""+self.name()+"""' . #identify this neuron
                    #?node2 rdfs:label '"""+item+"""' . #identify the argument
                    #GRAPH ?g { #Each triple is in its own sub-graph to enable provenance
                        ## find the triple that connects the neuron node to the receptor node
                        ## via the 'receptor' (361) relation
                        #?node <""" + t + """>?node2 .
                    #}
                  ##Triples with prov information are in the main graph only
                  ##For the sub-graph, find the prov associated
                  #?g <http://openworm.org/entities/text_reference> ?prov
            #}
            #""")

        #ref = []
        #for f in qres:
            #s = str(f['prov'])
            #if s != '':
                #ref.append(s)

        #return ref

    # Directed graph. Getting accessible _from_ this node

    def get_incidents(self, type=0):
        """ Get neurons which synapse at this neuron """
        for item in self['nx'].in_edges_iter(self.name(),data=True):
            if 'GapJunction' in item[2]['synapse']:
                yield item[0]

    def _as_neuroml(self):
       """Return this neuron as a NeuroML representation

          :rtype: libNeuroML.Neuron
       """
    #def rdf(self):

    #def peptides(self):


