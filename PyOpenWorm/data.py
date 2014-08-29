# A consolidation of the data sources for the project
# includes:
# NetworkX!
# RDFlib!
# Other things!
#
# Works like Configure:
# Inherit from the DataUser class to access data of all kinds (listed above)


import hashlib
from rdflib import URIRef, Literal, Graph, Namespace, ConjunctiveGraph
from rdflib.namespace import RDFS, RDF, NamespaceManager
from datetime import datetime as DT
import datetime
import transaction
import os
import traceback
import logging as L
from .configure import Configureable, Configure, ConfigValue, BadConf

__all__ = ["Data", "RDFSource", "SerializationSource", "TrixSource", "SPARQLSource", "SleepyCatSource", "DefaultSource", "ZODBSource"]

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
        self.link('molecule_name', 'new_graph_uri')
        self['molecule_name'] = self._molecule_hash

    @classmethod
    def open(cls,file_name):
        """ Open a file storing configuration in a JSON format """
        Configureable.conf = Configure.open(file_name)
        return cls()

    def openDatabase(self):
        """ Open a the configured database """
        self._init_rdf_graph()
        L.debug("opening " + str(self.source))
        self.source.open()
        nm = NamespaceManager(self['rdf.graph'])
        self['rdf.namespace_manager'] = nm
        self['rdf.graph'].namespace_manager = nm

        nm.bind("", self['rdf.namespace'])

    def closeDatabase(self):
        """ Close a the configured database """
        self.source.close()

    def _init_rdf_graph(self):
        # Set these in case they were left out
        c = self.conf
        self['rdf.source'] = c['rdf.source'] = c.get('rdf.source', 'default')
        self['rdf.store'] = c['rdf.store'] = c.get('rdf.store', 'default')
        self['rdf.store_conf'] = c['rdf.store_conf'] = c.get('rdf.store_conf', 'default')

        # XXX:The conf=self can probably be removed
        self.sources = {'sqlite' : SQLiteSource,
                'sparql_endpoint' : SPARQLSource,
                'sleepycat' : SleepyCatSource,
                'default' : DefaultSource,
                'trix' : TrixSource,
                'serialization' : SerializationSource,
                'zodb' : ZODBSource
                }
        i = self.sources[self['rdf.source'].lower()]()
        self.source = i
        self.link('semantic_net_new', 'semantic_net', 'rdf.graph')
        self['rdf.graph'] = i
        return i

    def _molecule_hash(self, data):
        return URIRef(self.molecule_namespace[hashlib.sha224(str(data)).hexdigest()])

    def _init_networkX(self):
        import networkx as nx
        import csv
        import urllib2
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

class RDFSource(ConfigValue,Configureable):
    """ Base class for data sources.

    Alternative sources should dervie from this class
    """
    def __init__(self, **kwargs):
        Configureable.__init__(self, **kwargs)
        ConfigValue.__init__(self, **kwargs)
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

    def open(self):
        """ Called on ``PyOpenWorm.connect()`` to set up and return the rdflib graph.
        Must be overridden by sub-classes.
        """
        raise NotImplementedError()

class SerializationSource(RDFSource):
    """ Reads from an RDF serialization or, if the configured database is more recent, then from that.

        The database store is configured with::

            "rdf.source" = "serialization"
            "rdf.store" = <your rdflib store name here>
            "rdf.serialization" = <your RDF serialization>
            "rdf.serialization_format" = <your rdflib serialization format used>
            "rdf.store_conf" = <your rdflib store configuration here>

    """

    def open(self):
        if not self.graph:
            self.graph = True
            import glob
            # Check the ages of the files. Read the more recent one.
            g0 = ConjunctiveGraph(store=self.conf['rdf.store'])
            database_store = self.conf['rdf.store_conf']
            source_file = self.conf['rdf.serialization']
            file_format = self.conf['rdf.serialization_format']
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

            trix_time = modification_date(source_file)

            g0.open(database_store, create=True)

            if store_time > trix_time:
                # just use the store
                pass
            else:
                # delete the database and read in the new one
                # read in the serialized format
                g0.parse(source_file,format=file_format)

            self.graph = g0

        return self.graph

class TrixSource(SerializationSource):
    """ A SerializationSource specialized for TriX

        The database store is configured with::

            "rdf.source" = "trix"
            "rdf.trix_location" = <location of the TriX file>
            "rdf.store" = <your rdflib store name here>
            "rdf.store_conf" = <your rdflib store configuration here>

    """
    def __init__(self,**kwargs):
        SerializationSource.__init__(self,**kwargs)
        h = self.conf.get('trix_location','UNSET')
        self.conf.link('rdf.serialization','trix_location')
        self.conf['rdf.serialization'] = h
        self.conf['rdf.serialization_format'] = 'trix'

class SPARQLSource(RDFSource):
    """ Reads from and queries against a remote data store

        ::

            "rdf.source" = "sparql_endpoint"
    """
    def open(self):
        # XXX: If we have a source that's read only, should we need to set the store separately??
        g0 = ConjunctiveGraph('SPARQLUpdateStore')
        g0.open(tuple(self.conf['rdf.store_conf']))
        self.graph = g0
        return self.graph

class SleepyCatSource(RDFSource):
    """ Reads from and queries against a local Sleepycat database

        The database can be configured like::

            "rdf.source" = "Sleepycat"
            "rdf.store_conf" = <your database location here>
    """
    def open(self):
        import logging
        # XXX: If we have a source that's read only, should we need to set the store separately??
        g0 = ConjunctiveGraph('Sleepycat')
        self.conf['rdf.store'] = 'Sleepycat'
        g0.open(self.conf['rdf.store_conf'],create=True)
        self.graph = g0
        logging.debug("Opened SleepyCatSource")


class SQLiteSource(RDFSource):
    """ Reads from and queries against a SQLite database

    See see the SQLite database :file:`db/celegans.db` for the format

    The database store is configured with::

        "rdf.source" = "Sleepycat"
        "sqldb" = "/home/USER/openworm/PyOpenWorm/db/celegans.db",
        "rdf.store" = <your rdflib store name here>
        "rdf.store_conf" = <your rdflib store configuration here>

    Leaving ``rdf.store`` unconfigured simply gives an in-memory data store.
    """
    def open(self):
        import sqlite3
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

class DefaultSource(RDFSource):
    """ Reads from and queries against a configured database.

        The default configuration.

        The database store is configured with::

            "rdf.source" = "default"
            "rdf.store" = <your rdflib store name here>
            "rdf.store_conf" = <your rdflib store configuration here>

        Leaving unconfigured simply gives an in-memory data store.
    """
    def open(self):
        self.graph = ConjunctiveGraph(self.conf['rdf.store'])
        self.graph.open(self.conf['rdf.store_conf'],create=True)

class ZODBSource(RDFSource):
    """ Reads from and queries against a configured Zope Object Database.

        If the configured database does not exist, it is created.

        The database store is configured with::

            "rdf.source" = "ZODB"
            "rdf.store_conf" = <location of your ZODB database>

        Leaving unconfigured simply gives an in-memory data store.
    """
    def __init__(self,*args,**kwargs):
        RDFSource.__init__(self,*args,**kwargs)
        self.conf['rdf.store'] = "ZODB"

    def open(self):
        import ZODB
        from ZODB.FileStorage import FileStorage
        self.path = self.conf['rdf.store_conf']
        openstr = os.path.abspath(self.path)

        fs=FileStorage(openstr)
        self.zdb=ZODB.DB(fs)
        self.conn=self.zdb.open()
        root=self.conn.root()
        if 'rdflib' not in root:
            root['rdflib'] = ConjunctiveGraph('ZODB')
        self.graph = root['rdflib']
        try:
            transaction.commit()
        except Exception as e:
            # catch commit exception and close db.
            # otherwise db would stay open and follow up tests
            # will detect the db in error state
            L.warning('Forced to abort transaction on ZODB store opening')
            traceback.print_exc()
            transaction.abort()
        transaction.begin()
        self.graph.open(self.path)


    def close(self):
        if self.graph == False:
            return

        self.graph.close()

        try:
            transaction.commit()
        except Exception as e:
            # catch commit exception and close db.
            # otherwise db would stay open and follow up tests
            # will detect the db in error state
            traceback.print_exc()
            L.warning('Forced to abort transaction on ZODB store closing')
            transaction.abort()
        self.conn.close()
        self.zdb.close()
        self.graph = False

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

