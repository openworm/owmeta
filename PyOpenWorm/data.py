from __future__ import print_function
import sqlite3
import hashlib
from rdflib import URIRef, Literal, Graph, Namespace, ConjunctiveGraph
from rdflib.namespace import RDFS, RDF, NamespaceManager
from datetime import datetime as DT
import datetime
import transaction
import os
import traceback
import logging
from .utils import grouper
from .configure import Configureable, Configure, ConfigValue

__all__ = [
    "Data",
    "DataUser",
    "RDFSource",
    "SerializationSource",
    "TrixSource",
    "SPARQLSource",
    "SleepyCatSource",
    "DefaultSource",
    "ZODBSource"]

L = logging.getLogger(__name__)


_B_UNSET = object()


class _B(ConfigValue):

    def __init__(self, f):
        self.v = _B_UNSET
        self.f = f

    def get(self):
        if self.v is _B_UNSET:
            self.v = self.f()

        return self.v

    def invalidate(self):
        self.v = None

    def __repr__(self):
        if self.v is _B_UNSET:
            return 'Thunk of ' + repr(self.f)
        return repr(self.v)


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


class DataUser(Configureable):

    """ A convenience wrapper for users of the database

    Classes which use the database should inherit from DataUser.
    """

    def __init__(self, *args, **kwargs):
        super(DataUser, self).__init__(*args, **kwargs)
        self.__base_namespace = None

    @property
    def base_namespace(self):
        if self.__base_namespace is not None:
            return self.__base_namespace
        return self.conf['rdf.namespace']

    @base_namespace.setter
    def base_namespace(self, value):
        self.__base_namespace = value

    @property
    def rdf(self):
        return self.conf['rdf.graph']

    @property
    def namespace_manager(self):
        return self.conf.get('rdf.namespace_manager', None)

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
        if self.conf['rdf.store'] == 'SPARQLUpdateStore':
            # XXX With Sesame, for instance, it is probably faster to do a PUT over
            # the endpoint's rest interface. Just need to do it for some common
            # endpoints

            try:
                gs = g.serialize(format="nt")
            except Exception:
                gs = _triples_to_bgp(g)

            if graph_name:
                s = " INSERT DATA { GRAPH " + graph_name.n3() + " {" + gs + " } } "
            else:
                s = " INSERT DATA { " + gs + " } "
                L.debug("update query = " + s)
                self.conf['rdf.graph'].update(s)
        else:
            gr = self.conf['rdf.graph']
            if self.conf['rdf.source'] == 'ZODB':
                transaction.commit()
                transaction.begin()
            for x in g:
                gr.add(x)
            if self.conf['rdf.source'] == 'ZODB':
                transaction.commit()
                transaction.begin()

        # infer from the added statements
        # self.infer()

    def infer(self):
        """ Fire FuXi rule engine to infer triples """

        from FuXi.Rete.RuleStore import SetupRuleStore
        from FuXi.Rete.Util import generateTokenSet
        from FuXi.Horn.HornRules import HornFromN3
        # fetch the derived object's graph
        semnet = self.rdf
        rule_store, rule_graph, network = SetupRuleStore(makeNetwork=True)
        closureDeltaGraph = Graph()
        network.inferredFacts = closureDeltaGraph
        # build a network of rules
        for rule in HornFromN3('testrules.n3'):
            network.buildNetworkFromClause(rule)
        # apply rules to original facts to infer new facts
        network.feedFactsToAdd(generateTokenSet(semnet))
        # combine original facts with inferred facts
        for x in closureDeltaGraph:
            self.rdf.add(x)

    def add_reference(self, g, reference_iri):
        """
        Add a citation to a set of statements in the database

        :param triples: A set of triples to annotate
        """
        new_statements = Graph()
        ns = self.conf['rdf.namespace']
        for statement in g:
            statement_node = self._reify(new_statements, statement)
            new_statements.add(
                (URIRef(reference_iri),
                 ns['asserts'],
                    statement_node))

        self.add_statements(g + new_statements)

    def retract_statements(self, graph):
        """
        Remove a set of statements from the database.

        :param graph: An iterable of triples
        """
        self._remove_from_store_by_query(graph)

    def _remove_from_store_by_query(self, q):
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

    def _reify(self, g, s):
        """
        Add a statement object to g that binds to s
        """
        n = self.conf['new_graph_uri'](s)
        g.add((n, RDF['type'], RDF['Statement']))
        g.add((n, RDF['subject'], s[0]))
        g.add((n, RDF['predicate'], s[1]))
        g.add((n, RDF['object'], s[2]))
        return n


class Data(Configure):

    """
    Provides configuration for access to the database.

    Usually doesn't need to be accessed directly
    """

    def __init__(self, conf=None, **kwargs):
        """
        Parameters
        ----------
        conf : Configure
            A Configure object
        """
        super(Data, self).__init__(**kwargs)

        if conf is not None:
            self.copy(conf)
        else:
            self.copy(Configureable.default)
        self.namespace = Namespace("http://openworm.org/entities/")
        self.molecule_namespace = Namespace("http://openworm.org/entities/molecules/")
        self['rdf.namespace'] = self.namespace
        self['molecule_name'] = self._molecule_hash
        self['new_graph_uri'] = self._molecule_hash

    @classmethod
    def load(cls, file_name):
        """ Load a file into a new Data instance storing configuration in a JSON format """
        return cls.open(file_name)

    @classmethod
    def open(cls, file_name):
        """ Load a file into a new Data instance storing configuration in a JSON format """
        return cls(conf=Configure.open(file_name))

    def openDatabase(self):
        self.init_database()

    def init_database(self):
        """ Open the configured database """
        self._init_rdf_graph()
        L.debug("opening " + str(self.source))
        self.source.open()
        nm = NamespaceManager(self['rdf.graph'])
        self['rdf.namespace_manager'] = nm
        self['rdf.graph'].namespace_manager = nm

        # A runtime version number for the graph should update for all changes
        # to the graph
        self['rdf.graph.change_counter'] = 0

        self['rdf.graph']._add = self['rdf.graph'].add
        self['rdf.graph']._remove = self['rdf.graph'].remove
        self['rdf.graph'].add = self._my_graph_add
        self['rdf.graph'].remove = self._my_graph_remove
        nm.bind("", self['rdf.namespace'])

    def _my_graph_add(self, triple):
        self['rdf.graph']._add(triple)

        # It's important that this happens _after_ the update otherwise anyone
        # checking could think they have the lastest version when they don't
        self['rdf.graph.change_counter'] += 1

    def _my_graph_remove(self, triple_or_quad):
        self['rdf.graph']._remove(triple_or_quad)

        # It's important that this happens _after_ the update otherwise anyone
        # checking could think they have the lastest version when they don't
        self['rdf.graph.change_counter'] += 1

    def closeDatabase(self):
        """ Close a the configured database """
        self.source.close()

    def _init_rdf_graph(self):
        # Set these in case they were left out
        self['rdf.source'] = self.get('rdf.source', 'default')
        self['rdf.store'] = self.get('rdf.store', 'default')
        self['rdf.store_conf'] = self.get('rdf.store_conf', 'default')

        # XXX:The conf=self can probably be removed
        self.sources = {'sqlite': SQLiteSource,
                        'sparql_endpoint': SPARQLSource,
                        'sleepycat': SleepyCatSource,
                        'default': DefaultSource,
                        'trix': TrixSource,
                        'serialization': SerializationSource,
                        'zodb': ZODBSource}
        source = self.sources[self['rdf.source'].lower()](conf=self)
        self.source = source

        self.link('semantic_net_new', 'semantic_net', 'rdf.graph')
        self['rdf.graph'] = source
        return source

    def _molecule_hash(self, data):
        return URIRef(
            self.molecule_namespace[
                hashlib.sha224(
                    str(data)).hexdigest()])

    def __setitem__(self, k, v):
        return Configure.__setitem__(self, k, v)

    def __getitem__(self, k):
        return Configure.__getitem__(self, k)


def modification_date(filename):
    t = os.path.getmtime(filename)
    return datetime.datetime.fromtimestamp(t)


class RDFSource(Configureable, ConfigValue):

    """ Base class for data sources.

    Alternative sources should dervie from this class
    """

    def __init__(self, **kwargs):
        super(RDFSource, self).__init__(**kwargs)
        self.graph = False

    def get(self):
        if self.graph is False:
            raise Exception(
                "Must call openDatabase on Data object before using the database")
        return self.graph

    def close(self):
        if self.graph is False:
            return
        self.graph.close()
        self.graph = False

    def open(self):
        """ Called on ``PyOpenWorm.connect()`` to set up and return the rdflib graph.
        Must be overridden by sub-classes.
        """
        raise NotImplementedError()


class SerializationSource(RDFSource):

    """ Reads from an RDF serialization or, if the configured database is more
        recent, then from that.

        The database store is configured with::

            "rdf.source" = "serialization"
            "rdf.store" = <your rdflib store name here>
            "rdf.serialization" = <your RDF serialization>
            "rdf.serialization_format" = <rdflib serialization format>
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
                for x in glob.glob(database_store + "/*"):
                    mod = modification_date(x)
                    if store_time < mod:
                        store_time = mod
            except Exception:
                store_time = DT.min

            trix_time = modification_date(source_file)

            g0.open(database_store, create=True)

            if store_time > trix_time:
                # just use the store
                pass
            else:
                # delete the database and read in the new one
                # read in the serialized format
                g0.parse(source_file, format=file_format)

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

    def __init__(self, **kwargs):
        SerializationSource.__init__(self, **kwargs)
        h = self.conf.get('trix_location', 'UNSET')
        self.conf.link('rdf.serialization', 'trix_location')
        self.conf['rdf.serialization'] = h
        self.conf['rdf.serialization_format'] = 'trix'


def _rdf_literal_to_gp(x):
    return x.n3()


def _triples_to_bgp(trips):
    # XXX: Collisions could result between the variable names of different
    # objects
    g = " .\n".join(" ".join(_rdf_literal_to_gp(x) for x in y) for y in trips)
    return g


class SPARQLSource(RDFSource):

    """ Reads from and queries against a remote data store

        ::

            "rdf.source" = "sparql_endpoint"
    """

    def open(self):
        # XXX: If we have a source that's read only, should we need to set the
        # store separately??
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
        # XXX: If we have a source that's read only, should we need to set the
        # store separately??
        g0 = ConjunctiveGraph('Sleepycat')
        self.conf['rdf.store'] = 'Sleepycat'
        g0.open(self.conf['rdf.store_conf'], create=True)
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
        conn = sqlite3.connect(self.conf['sqldb'])
        cur = conn.cursor()

        # first step, grab all entities and add them to the graph
        n = self.conf['rdf.namespace']

        cur.execute("SELECT DISTINCT ID, Entity FROM tblentity")
        g0 = ConjunctiveGraph(self.conf['rdf.store'])
        g0.open(self.conf['rdf.store_conf'], create=True)

        for r in cur.fetchall():
            # first item is a number -- needs to be converted to a string
            first = str(r[0])
            # second item is text
            second = str(r[1])

            # This is the backbone of any RDF graph.  The unique
            # ID for each entity is encoded as a URI and every other piece of
            # knowledge about that entity is connected via triples to that URI
            # In this case, we connect the common name of that entity to the
            # root URI via the RDFS label property.
            g0.add((n[first], RDFS.label, Literal(second)))

        # second step, get the relationships between them and add them to the
        # graph
        cur.execute(
            "SELECT DISTINCT EnID1, Relation, EnID2, Citations FROM tblrelationship")

        gi = ''

        i = 0
        for r in cur.fetchall():
            # all items are numbers -- need to be converted to a string
            first = str(r[0])
            second = str(r[1])
            third = str(r[2])
            prov = str(r[3])

            ui = self.conf['molecule_name'](prov)
            gi = Graph(g0.store, ui)

            gi.add((n[first], n[second], n[third]))

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
        self.graph.open(self.conf['rdf.store_conf'], create=True)


class ZODBSource(RDFSource):

    """ Reads from and queries against a configured Zope Object Database.

        If the configured database does not exist, it is created.

        The database store is configured with::

            "rdf.source" = "ZODB"
            "rdf.store_conf" = <location of your ZODB database>

        Leaving unconfigured simply gives an in-memory data store.
    """

    def __init__(self, *args, **kwargs):
        super(ZODBSource, self).__init__(*args, **kwargs)
        self.conf['rdf.store'] = "ZODB"

    def open(self):
        import ZODB
        from ZODB.FileStorage import FileStorage
        self.path = self.conf['rdf.store_conf']
        openstr = os.path.abspath(self.path)

        fs = FileStorage(openstr)
        self.zdb = ZODB.DB(fs, cache_size=1600)
        self.conn = self.zdb.open()
        root = self.conn.root()
        if 'rdflib' not in root:
            root['rdflib'] = ConjunctiveGraph('ZODB')
        self.graph = root['rdflib']
        try:
            transaction.commit()
        except Exception:
            # catch commit exception and close db.
            # otherwise db would stay open and follow up tests
            # will detect the db in error state
            L.warning('Forced to abort transaction on ZODB store opening')
            traceback.print_exc()
            transaction.abort()
        transaction.begin()
        self.graph.open(self.path)

    def close(self):
        if self.graph is False:
            return

        self.graph.close()

        try:
            transaction.commit()
        except Exception:
            # catch commit exception and close db.
            # otherwise db would stay open and follow up tests
            # will detect the db in error state
            traceback.print_exc()
            L.warning('Forced to abort transaction on ZODB store closing')
            transaction.abort()
        self.conn.close()
        self.zdb.close()
        self.graph = False
