
# A consolidation of the data sources for the project
# includes:
# NetworkX!
# RDFlib!
# Other things!
#
# Works like Configure:
# Inherit from the Data class to access data of all kinds (listed above)

import sqlite3
import networkx as nx
import PyOpenWorm
from PyOpenWorm import Configureable, Configure, ConfigValue
import hashlib
import csv
import urllib2
from rdflib import URIRef, Literal, Graph, Namespace, ConjunctiveGraph, BNode
from rdflib.plugins.stores.sparqlstore import SPARQLStore
from rdflib.namespace import RDFS,RDF
from datetime import datetime as DT
import pytz
from rdflib.namespace import XSD

# encapsulates some of the data all of the parts need...
class _B(ConfigValue):
    def __init__(self, f):
        self.v = False
        self.f = f

    def get(self):
        if not self.v:
            self.v = self.f()

        return self.v
    def invalidate(self):
        self.v = False

class _Z(ConfigValue):
    def __init__(self, c, n):
        self.n = n
    def get(self):
        return c[n]

propertyTypes = {"send" : 'http://openworm.org/entities/356',
        "Neuropeptide" : 'http://openworm.org/entities/354',
        "Receptor" : 'http://openworm.org/entities/361',
        "is a" : 'http://openworm.org/entities/1515',
        "neuromuscular junction" : 'http://openworm.org/entities/1516',
        "Innexin" : 'http://openworm.org/entities/355',
        "Neurotransmitter" : 'http://openworm.org/entities/313',
        "gap junction" : 'http://openworm.org/entities/357'}

class DataUser(Configureable):
    def __init__(self, conf = False):
        if isinstance(conf, Data):
            Configureable.__init__(self, conf)
        else:
            Configureable.__init__(self, Data(conf))

    def _add_to_store(self, g, graph_name=False):
        if not graph_name:
            graph_name = g.identifier
        self.conf['rdf.graph'].update(" INSERT DATA { GRAPH "+graph_name.n3()+" { " + g.serialize(format="nt") + "} } ")
        return g

    def add_reference(self, triples, reference_iri):
        """
        Add a citation to a set of statements in the database
        Annotates the addition with uploader name, etc
        :param triples: A set of triples to annotate
        """
        g0 = ConjunctiveGraph()
        g = Graph(g0.store, identifier=reference_iri)
        ns = self.conf['rdf.namespace']
        g0.add((reference_iri, RDF['type'], ns['misc_reference']))
        self.add_statements(g0)

    def add_statements(self, graph):
        """
        Add a set of statements the database.
        Annotates the addition with uploader name, etc
        :param triples_or_graph: A set of triples or a rdflib graph to add
        """
        uri = self.conf['molecule_name'](graph.identifier)
        g = self._add_to_store(graph, uri)

        #XXX: We should maybe check that this has the correct format
        time_stamp = DT.now(pytz.utc).isoformat()
        ns = self.conf['rdf.namespace']
        gr = self.conf['rdf.graph']

        gr.add((uri, ns['upload_date'], Literal(time_stamp, datatype=XSD['dateTimeStamp']), None))
        gr.add((uri, ns['uploader'], Literal(self.conf['user.email']), None))

class Data(Configure, Configureable):
    def __init__(self, conf=False):
        Configureable.__init__(self,conf)
        Configure.__init__(self)
        self.namespace = Namespace("http://openworm.org/entities/")
        self['nx'] = _B(self._init_networkX)
        self['rdf.namespace'] = self.namespace
        self['molecule_name'] = self._molecule_hash
        self._init_rdf_graph()


    def _init_rdf_graph(self):
        # check rdf.source
        self['rdf.store'] = self.conf.get('rdf.store', 'default')
        self['rdf.store_conf'] = self.conf.get('rdf.store_conf', 'default')
        d = {'sqlite' : SQLiteSource(self),
                'sparql_endpoint' : SPARQLSource(self)}
        i = d[self.conf['rdf.source']]
        self['rdf.graph'] = i
        self['semantic_net_new'] = i
        self['semantic_net'] = i
        return i

    def _molecule_hash(self, data):
        return URIRef(u'http://openworm.org/rdfmolecules/' + hashlib.sha224(data).hexdigest())

    def _init_networkX(self):
        g = nx.DiGraph()

        # Neuron table
        csvfile = urllib2.urlopen(self.conf['neuronscsv'])

        reader = csv.reader(csvfile, delimiter=';', quotechar='|')
        for row in reader:
            neurontype = ""
            # Detects neuron function
            if "sensory" in row[1].lower():
                neurontype += "sensory"
            if "motor" in row[1].lower():
                neurontype += "motor"
            if "interneuron" in row[1].lower():
                neurontype += "interneuron"
            if len(neurontype) == 0:
                neurontype = "unknown"

            if len(row[0]) > 0: # Only saves valid neuron names
                g.add_node(row[0], ntype = neurontype)

        # Connectome table
        csvfile = urllib2.urlopen(self.conf['connectomecsv'])

        reader = csv.reader(csvfile, delimiter=';', quotechar='|')
        for row in reader:
            g.add_edge(row[0], row[1], weight = row[3])
            g[row[0]][row[1]]['synapse'] = row[2]
            g[row[0]][row[1]]['neurotransmitter'] = row[4]
        return g

class SPARQLSource(Configureable,PyOpenWorm.ConfigValue):
    def get(self):
        # XXX: If we have a source that's read only, should we need to set the store separately??
        g0 = ConjunctiveGraph('SPARQLUpdateStore')
        g0.open(self.conf['rdf.store_conf'])
        return g0

class SQLiteSource(Configureable,PyOpenWorm.ConfigValue):
    def get(self):
        conn = sqlite3.connect(self.conf['sqldb'])
        cur = conn.cursor()

        #first step, grab all entities and add them to the graph
        n = self.conf['rdf.namespace']

        cur.execute("SELECT DISTINCT ID, Entity FROM tblentity")


        # print cur.description

        g0 = ConjunctiveGraph(self.conf['rdf.store'])
        #print self['rdf.store']
        g0.open(self.conf['rdf.store_conf'], create=True)

        for r in cur.fetchall():
            #first item is a number -- needs to be converted to a string
           first = str(r[0])
           #second item is text
           second = str(r[1])

           # This is the backbone of any RDF graph.  The unique
           # ID for each entity is encoded as a URI and every other piece of
           # knowledge about that entity is connected via triples to that URI
           # In this case, we connect the common name of that entity to the
           # root URI via the RDFS label property.
           g0.add( (n[first], RDFS.label, Literal(second)) )


        #second step, get the relationships between them and add them to the graph
        cur.execute("SELECT DISTINCT EnID1, Relation, EnID2, Citations FROM tblrelationship")

        gi = ''

        i = 0
        for r in cur.fetchall():
           #all items are numbers -- need to be converted to a string
           first = str(r[0])
           second = str(r[1])
           third = str(r[2])
           prov = str(r[3])

           ui = self.conf['molecule_name'](prov)
           gi = Graph(g0.store, ui)

           gi.add( (n[first], n[second], n[third]) )

           g0.add([ui, RDFS.label, Literal(str(i))])
           if (prov != ''):
               g0.add([ui, n[u'text_reference'], Literal(prov)])

           i = i + 1

        cur.close()
        conn.close()

        return g0

