"""
.. class:: Neuron

   neuron client
   =============

   This module contains the class that defines the neuron

"""

import sqlite3
from rdflib import Graph, Namespace, ConjunctiveGraph, BNode, URIRef, Literal
from rdflib.namespace import RDFS
import PyOpenWorm as P
from PyOpenWorm import Cell, DataUser, Configure, propertyTypes


# XXX: Should we specify somewhere whether we have NetworkX or something else?

class Neighbor(P.Property):
    """Get a list of neighboring neurons.

       :param type: What kind of junction to look for.
                    0=all, 1=gap junctions only, 2=all chemical synapses
                    3=incoming chemical synapses, 4=outgoing chemical synapses
       :returns: a list of neuron names
       :rtype: List
    """
    def __init__(self,**kwargs):
        P.Property.__init__(self,**kwargs)
        self._conns = []

    def get(self,**kwargs):
        c = P.Connection(pre_cell=self.owner,**kwargs)
        for r in c.load():
            yield r.post_cell()

    def set(self, other, **kwargs):
        c = P.Connection(pre_cell=self,post_cell=other,**kwargs)
        self._conns.append(c)
        # should just save the triples for saving later...

    def triples(self):
        for c in self._conns:
            for x in c.triples():
                yield x

class Neuron(Cell):
    def __init__(self, **kwargs):
        Cell.__init__(self,**kwargs)
        self.neighbor = Neighbor(owner=self)
        self.get_neighbors = self.neighbor

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

    def type(self):
        """Get type of this neuron (motor, interneuron, sensory)

        :returns: the type
        :rtype: str
        """
        return self._type_networkX().lower()

    def receptors(self):
        """Get receptors associated with this neuron

        :returns: a list of all known receptors
        :rtype: list
        """
        q = """SELECT ?objLabel     #we want to get out the labels associated with the objects
           WHERE {
                    #we are looking first for the node that is the anchor of
                    # all information about the specified neuron
              ?node ?p ?name .
                    # having identified that node, here we match an object
                    #  associated with the node via the 'receptor' property
                    #  (number 361)
              ?node <http://openworm.org/entities/361> ?object .
                    #for the object, look up their plain text label.
              ?object rdfs:label ?objLabel .
              FILTER( ?name in ("""+ ", ".join("'%s'" % x for x in self.name()) + """) )
            }"""
        print q
        qres = self['rdf.graph'].query(q)

        receptors = []
        for r in qres.result:
            receptors.append(str(r[0]))

        return receptors

    def add_reference(self, type, item, pmid = None, doi = None, wormbaseid = None):
        """Add a reference that provides evidence of the relationship between
            this neuron and one of its elements.

            Example::

                >>>aval = PyOpenWorm.Neuron('AVAL')
               >>>aval.receptors()
               ['GLR-1', 'NMR-1', 'GLR-4', 'GLR-2', 'GGR-3', 'UNC-8', 'GLR-5', 'NMR-2']
               #look up what reference says this neuron has a receptor GLR-1
               >>>aval.get_reference(0,'GLR-1')
               None
                   >>>aval.add_reference(0,'GLR-1', doi='125.41.3/ploscompbiol',
                           pmid = '57182010')
                   >>>aval.get_reference(0,'GLR-1')
                   ['http://dx.doi.org/125.41.3/ploscompbiol', 'http://pubmedcentral.nih.gov/57182010']
        :param type: The kind of thing to add.  Valid options are: 0=receptor, 1=neighbor
        :param item: Name of the item
            :param doi: A Digital Object Identifier (DOI) that provides evidence, optional
            :param pmid: A PubMed ID (PMID) that point to a paper that provides evidence, optional
            :param wormbaseid: An ID from WormBase that points to a record that provides evidence, optional
        """

        try:
            t = propertyTypes[type]
        except KeyError:
            # XXX: need logging
            print 'not a valid type ' + type
            return

        qres = self['rdf.graph'].query(
          """SELECT ?this ?p ?that
           WHERE {
              ?this rdfs:label '"""+self.name()+"""' .
              ?that rdfs:label '"""+item +"""' .
              ?this <"""+t+"""> ?that .
              bind (<"""+t+"""> as ?p)
            }""")
        if len(qres) > 0:
            #XXX: Should verify that we're given a valid uri
            ui = self['molecule_name'](pmid)
            DataUser.add_reference(self, [qres], ui)

    def check_exists(self):
        """Ask if the neuron already exists
        """
        r = self['rdf.graph'].query("ASK { ?node <http://openworm.org/entities/1515> <http://openworm.org/entities/1> . ?node rdfs:label '"+self.name()+"'}")
        return r.askAnswer


    def get_reference(self, type, item=''):
        """Get a reference back that provides the evidence that this neuron is
           associated with the item requested as a list of URLs.

           Example::

               >>>ader = PyOpenWorm.Neuron('ADER')
               >>>ader.receptors()
             ['ACR-16', 'TYRA-3', 'DOP-2', 'EXP-1']
               #look up what reference says this neuron has a receptor EXP-1
               >>>ader.get_reference(0,'EXP-1')
               ['http://dx.doi.org/10.100.123/natneuro']
               #look up what reference says this neuron has a neighbor DD5
               >>>ader.get_reference(1, 'DD5')
               ['http://dx.doi.org/20.140.521/ploscompbiol']

           :param type: The kind of thing to search for.  Valid options are: 0=receptor, 1=neighbor
           :param item: Name of the item requested, if appropriate
           :returns: a list of URLs that points to references
           :rtype: list
        """
        try:
            t = propertyTypes[type]
        except KeyError:
            # XXX: need logging
            print 'not a valid type ' + str(type)
            return

        qres = self['rdf.graph'].query(
            """
            SELECT ?prov #we want to get out the labels associated with the objects
            WHERE {
                    ?node rdfs:label '"""+self.name()+"""' . #identify this neuron
                    ?node2 rdfs:label '"""+item+"""' . #identify the argument
                    GRAPH ?g { #Each triple is in its own sub-graph to enable provenance
                        # find the triple that connects the neuron node to the receptor node
                        # via the 'receptor' (361) relation
                        ?node <""" + t + """>?node2 .
                    }
                  #Triples with prov information are in the main graph only
                  #For the sub-graph, find the prov associated
                  ?g <http://openworm.org/entities/text_reference> ?prov
            }
            """)

        ref = []
        for f in qres:
            s = str(f['prov'])
            if s != '':
                ref.append(s)

        return ref

    # Directed graph. Getting accessible _from_ this node

    def get_incidents(self, type=0):
        for item in self['nx'].in_edges_iter(self.name(),data=True):
            if 'GapJunction' in item[2]['synapse']:
                yield item[0]

    def _get_connections(self, type=0):
        """Get a list of Connections between this neuron and other neurons.

           :param type: What kind of junction to look for.
                        0=all, 1=gap junctions only, 2=all chemical synapses
                        3=incoming chemical synapses, 4=outgoing chemical synapses
           :returns: a list of PyOpenWorm.Connection objects
           :rtype: List
           """


    def _as_neuroml(self):
       """Return this neuron as a NeuroML representation

          :rtype: libNeuroML.Neuron
       """
    def __repr__(self):
        return "Neuron(name=%s)" % self.name()
    #def rdf(self):

    #def peptides(self):


