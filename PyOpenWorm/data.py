
# A consolidation of the data sources for the project
# includes:
# NetworkX!
# RDFlib!
# Other things!
#
# Works like Configure:
# Inherit from the DataUser class to access data of all kinds (listed above)

import sqlite3
import networkx as nx
import PyOpenWorm
from PyOpenWorm import Configureable, Configure, ConfigValue, BadConf
import hashlib
import csv
import urllib2
from rdflib import URIRef, Literal, Graph, Namespace, ConjunctiveGraph
from rdflib.namespace import RDFS,RDF
from datetime import datetime as DT
import datetime
import os
import logging as L

__all__ = ["Data", "DataUser", "RDFSource", "TrixSource", "SPARQLSource", "SleepyCatSource", "DefaultSource"]

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

ZERO = datetime.timedelta(0)
class _UTC(datetime.tzinfo):
    """UTC"""

    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZERO
utc = _UTC()

propertyTypes = {"send" : 'http://openworm.org/entities/356',
        "Neuropeptide" : 'http://openworm.org/entities/354',
        "Receptor" : 'http://openworm.org/entities/361',
        "is a" : 'http://openworm.org/entities/1515',
        "neuromuscular junction" : 'http://openworm.org/entities/1516',
        "Innexin" : 'http://openworm.org/entities/355',
        "Neurotransmitter" : 'http://openworm.org/entities/313',
        "gap junction" : 'http://openworm.org/entities/357'}

def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
    args = [iter(iterable)] * n
    while True:
        l = []
        try:
            for x in args:
                l.append(next(x))
        except:
            pass
        yield l
        if len(l) < n:
            break

class DataUser(Configureable):
    def __init__(self, conf = False):
        """ An convenience wrapper for users of the database

        Classes which use the database should inherit from DataUser.
        """
        Configureable.__init__(self, conf=conf)
        if not isinstance(self.conf,Data):
            raise BadConf(self)

    @property
    def base_namespace(self):
        return self.conf['rdf.namespace']

    @base_namespace.setter
    def base_namespace(self, value):
        self.conf['rdf.namespace'] = value

    @property
    def rdf(self):
        return self.conf['rdf.graph']

    @rdf.setter
    def rdf(self, value):
        self.conf['rdf.graph'] = value

    def _remove_from_store(self, g):
        # Note the assymetry with _add_to_store. You must add actual elements, but deletes
        # can be performed as a query
        for group in grouper(g, 1000):
            temp_graph = Graph()
            for x in group:
                if x is not None:
                    temp_graph.add(x)
                else:
                    break
            s = " DELETE DATA {" + temp_graph.serialize(format="nt") + " } "
            L.debug("deleting. s = " + s)
            self.conf['rdf.graph'].update(s)

    def _add_to_store(self, g, graph_name=False):
        for group in grouper(g, int(self.conf.get('rdf.upload_block_statement_count',100))):
            temp_graph = Graph()
            for x in group:
                if x is not None:
                    temp_graph.add(x)
                else:
                    break
            if graph_name:
                s = " INSERT DATA { GRAPH "+graph_name.n3()+" {" + temp_graph.serialize(format="nt") + " } } "
            else:
                s = " INSERT DATA { " + temp_graph.serialize(format="nt") + " } "
            L.debug("update query = " + s)
            self.conf['rdf.graph'].update(s)

    def add_reference(self, g, reference_iri):
        """
        Add a citation to a set of statements in the database
        :param triples: A set of triples to annotate
        """
        new_statements = Graph()
        ns = self.conf['rdf.namespace']
        for statement in g:
            statement_node = self._reify(new_statements,statement)
            new_statements.add((URIRef(reference_iri), ns['asserts'], statement_node))

        self.add_statements(g + new_statements)

    #def _add_unannotated_statements(self, graph):
    # A UTC class.

    def retract_statements(self, graph):
        """
        Remove a set of statements from the database.
        :param graph: An iterable of triples
        """
        self._remove_from_store_by_query(graph)
    def _remove_from_store_by_query(self, q):
        import logging as L
        s = " DELETE WHERE {" + q + " } "
        L.debug("deleting. s = " + s)
        self.conf['rdf.graph'].update(s)

    def add_statements(self, graph):
        """
        Add a set of statements to the database.
        Annotates the addition with uploader name, etc
        :param graph: An iterable of triples
        """
        self._add_to_store(graph)

    def _reify(self,g,s):
        """
        Add a statement object to g that binds to s
        """
        n = self.conf['new_graph_uri'](s)
        g.add((n, RDF['type'], RDF['Statement']))
        g.add((n, RDF['subject'], s[0]))
        g.add((n, RDF['predicate'], s[1]))
        g.add((n, RDF['object'], s[2]))
        return n


class Data(Configure, Configureable):
    """
    Provides configuration for access to the database.

    Usally doesn't need to be accessed directly
    """
    def __init__(self, conf=False):
        Configure.__init__(self)
        Configureable.__init__(self,conf)
        # We copy over all of the configuration that we were given
        self.copy(self.conf)
        self.namespace = Namespace("http://openworm.org/entities/")
        self.molecule_namespace = Namespace("http://openworm.org/entities/molecules/")
        self['nx'] = _B(self._init_networkX)
        self['rdf.namespace'] = self.namespace
        self['molecule_name'] = self._molecule_hash
        self['new_graph_uri'] = self._molecule_hash
        self._init_rdf_graph()

    @classmethod
    def open(cls,file_name):
        """ Open a file storing configuration in a JSON format """
        Configureable.conf = Configure.open(file_name)
        return cls()

    def openDatabase(self):
        """ Open a the configured database """
        L.debug("opening " + str(self.source))
        self.source.open()

    def closeDatabase(self):
        """ Close a the configured database """
        self.source.close()

    def _init_rdf_graph(self):
        # Set these in case they were left out
        c = self.conf
        self['rdf.source'] = c.get('rdf.source', 'default')
        self['rdf.store'] = c.get('rdf.store', 'default')
        self['rdf.store_conf'] = c.get('rdf.store_conf', 'default')

        self.sources = {'sqlite' : SQLiteSource(self),
                'sparql_endpoint' : SPARQLSource(self),
                'Sleepycat' : SleepyCatSource(self),
                'default' : DefaultSource(self),
                'TriX' : TrixSource(self)}
        i = self.sources[self['rdf.source']]
        self.source = i
        self.link('semantic_net_new', 'semantic_net', 'rdf.graph')
        self['rdf.graph'] = i
        return i

    def _molecule_hash(self, data):
        return URIRef(self.molecule_namespace[hashlib.sha224(str(data)).hexdigest()])

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

def modification_date(filename):
    t = os.path.getmtime(filename)
    return datetime.datetime.fromtimestamp(t)

class RDFSource(Configureable,PyOpenWorm.ConfigValue):
    """ Base class for data sources.

    Alternative sources should dervie from this class
    """
    i = 0
    def __init__(self, conf=False):
        if self.i == 1:
            raise Exception(self.i)
        self.i+=1
        Configureable.__init__(self, conf=conf)
        self.graph = False

    def get(self):
        if self.graph == False:
            raise Exception("Must call openDatabase on Data object before using the database")
        return self.graph

    def close(self):
        if self.graph == False:
            return
        self.graph.close()
        self.graph = False

class TrixSource(RDFSource):
    """ Reads from a TriX file or the configured store is more recent, from that.

    .. note::

        configure with  "rdf.source" = "TriX"

        The database store is configured with::

            "rdf.store" = <your rdflib store name here>
            "rdf.store_conf" = <your rdflib store configuration here>

    """
    # XXX How to write back out to this?
    i = 0

    def open(self):
        if not self.graph:
            self.graph = True
            import glob
            # Check the ages of the files. Read the more recent one.
            g0 = ConjunctiveGraph(store=self.conf['rdf.store'])
            database_store = self.conf['rdf.store_conf']
            trix_file = self.conf['trix_location']
            # store_time only works for stores that are on the local
            # machine.
            try:
                store_time = modification_date(database_store)
                # If the store is newer than the serialization
                # get the newest file in the store
                for x in glob.glob(database_store +"/*"):
                    mod = modification_date(x)
                    if store_time < mod:
                        store_time = mod
            except:
                store_time = DT.min

            trix_time = modification_date(trix_file)

            g0.open(database_store, create=True)

            if store_time > trix_time:
                # just use the store
                pass
            else:
                # delete the database and read in the new one
                # read in the serialized format
                g0.parse(trix_file,format="trix")

            self.graph = g0

        return self.graph

class SPARQLSource(RDFSource):
    """ Reads from and queries against a remote data store

        .. note::

            configure with  "rdf.source" = "sparql_endpoint"
    """
    def open(self):
        # XXX: If we have a source that's read only, should we need to set the store separately??
        g0 = ConjunctiveGraph('SPARQLUpdateStore')
        g0.open(tuple(self.conf['rdf.store_conf']))
        self.graph = g0
        return self.graph

class SleepyCatSource(RDFSource):
    """ Reads from and queries against a local Sleepycat database

        .. note:: configure with  "rdf.source" = "SQLiteSource"

        The database location can be configured like::

            "rdf.store_conf" = <your database location here>
    """
    def open(self):
        import logging
        # XXX: If we have a source that's read only, should we need to set the store separately??
        g0 = ConjunctiveGraph('Sleepycat')
        g0.open(self.conf['rdf.store_conf'],create=True)
        self.graph = g0
        logging.debug("Opened SleepyCatSource")


class SQLiteSource(RDFSource):
    def open(self):
        conn = sqlite3.connect(self.conf['sqldb'])
        cur = conn.cursor()

        #first step, grab all entities and add them to the graph
        n = self.conf['rdf.namespace']

        cur.execute("SELECT DISTINCT ID, Entity FROM tblentity")
        g0 = ConjunctiveGraph(self.conf['rdf.store'])
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
        self.graph = g0

class DefaultSource(RDFSource,ConfigValue):
    """ Reads from and queries against a configured database.

    .. note::

        The default configuration.

        Can also configure with "rdf.source" = "default"

        The database store is configured with::

            "rdf.store" = <your rdflib store name here>
            "rdf.store_conf" = <your rdflib store configuration here>

        Leaving unconfigured simply gives an in-memory data store.
    """
    def open(self):
        self.graph = ConjunctiveGraph(self.conf['rdf.store'])
        self.graph.open(self.conf['rdf.store_conf'],create=True)
