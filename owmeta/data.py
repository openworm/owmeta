from __future__ import print_function
import importlib as IM
import datetime
import os
import logging
import atexit
import hashlib
from datetime import datetime as DT

from rdflib import URIRef, Literal, Graph, Namespace, ConjunctiveGraph, plugin
from rdflib.store import TripleAddedEvent, TripleRemovedEvent, Store
from rdflib.events import Event
from rdflib.namespace import RDFS, RDF, NamespaceManager
import transaction

from .utils import grouper
from .configure import Configureable, Configure, ConfigValue

__all__ = [
    "Data",
    "DataUser",
    "RDFSource",
    "SPARQLSource",
    "SleepyCatSource",
    "DefaultSource",
    "ZODBSource",
    "SQLiteSource",
    "MySQLSource",
    "PostgreSQLSource"]

L = logging.getLogger(__name__)

ALLOW_UNCONNECTED_DATA_USERS = True


_B_UNSET = object()


ACTIVE_CONNECTIONS = []


def close_databases():
    for conn in ACTIVE_CONNECTIONS:
        conn.closeDatabase()


atexit.register(close_databases)


class OpenFailError(Exception):
    pass


class DatabaseConflict(Exception):
    pass


class DataUserUnconnected(Exception):
    def __init__(self, msg):
        super(DataUserUnconnected, self).__init__(str(msg) + ': No connection has been made for this data'
        ' user (i.e., it is unconfigured)')


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
        try:
            return self.conf['rdf.graph']
        except KeyError:
            if ALLOW_UNCONNECTED_DATA_USERS:
                return ConjunctiveGraph()
            raise DataUserUnconnected('No rdf.graph')

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
            self.copy(Configureable.default_config)
        self.namespace = Namespace("http://openworm.org/entities/")
        self.molecule_namespace = Namespace("http://openworm.org/entities/molecules/")
        self['rdf.namespace'] = self.namespace
        self['molecule_name'] = self._molecule_hash
        self['new_graph_uri'] = self._molecule_hash

        self._cch = None
        self._listeners = dict()

    @classmethod
    def load(cls, file_name):
        """ Load a file into a new Data instance storing configuration in a JSON format """
        return cls.open(file_name)

    @classmethod
    def open(cls, file_name):
        """ Load a file into a new Data instance storing configuration in a JSON format """
        return cls(conf=Configure.open(file_name))

    @classmethod
    def process_config(cls, config_dict, **kwargs):
        """ Load a file into a new Data instance storing configuration in a JSON format """
        return cls(conf=Configure.process_config(config_dict, **kwargs))

    def init(self):
        """ Open the configured database """
        self._init_rdf_graph()
        L.debug("opening " + str(self.source))
        try:
            self.source.open()
        except OpenFailError as e:
            L.error('Failed to open the data source because: %s', e)
            raise

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
        try:
            nm.bind("", self['rdf.namespace'])
        except Exception:
            L.warning("Failed to bind default RDF namespace %s", self['rdf.namespace'], exc_info=True)

    def openDatabase(self):
        self.init()
        ACTIVE_CONNECTIONS.append(self)

    init_database = init

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

    def destroy(self):
        """ Close a the configured database """
        self.source.close()
        try:
            ACTIVE_CONNECTIONS.remove(self)
        except ValueError:
            L.debug("Attempted to close a database which was already closed")

    closeDatabase = destroy

    def _init_rdf_graph(self):
        # Set these in case they were left out
        self['rdf.source'] = self.get('rdf.source', 'default')
        self['rdf.store'] = self.get('rdf.store', 'default')
        self['rdf.store_conf'] = self.get('rdf.store_conf', 'default')

        # XXX:The conf=self can probably be removed
        self.sources = {'sparql_endpoint': SPARQLSource,
                        'sleepycat': SleepyCatSource,
                        'default': DefaultSource,
                        'zodb': ZODBSource,
                        'sqlite': SQLiteSource,
                        'mysql': MySQLSource,
                        'postgresql': PostgreSQLSource}
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


class ContextChangedEvent(Event):
    pass


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
        """ Called on ``owmeta.connect()`` to set up and return the rdflib graph.
        Must be overridden by sub-classes.
        """
        raise NotImplementedError()


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


class ZODBSourceOpenFailError(OpenFailError):
    def __init__(self, openstr, *args):
        super(ZODBSourceOpenFailError, self).__init__('Could not open the database file "{}"'.format(openstr),
                                                      *args)
        self.openstr = openstr


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
        from zc.lockfile import LockError
        self.path = self.conf['rdf.store_conf']
        openstr = os.path.abspath(self.path)

        try:
            fs = FileStorage(openstr)
        except IOError:
            L.exception("Failed to create a FileStorage")
            raise ZODBSourceOpenFailError(openstr)
        except LockError:
            L.exception('Found database "{}" is locked when trying to open it. '
                    'The PID of this process: {}'.format(openstr, os.getpid()), exc_info=True)
            raise DatabaseConflict('Database ' + openstr + ' locked')

        self.zdb = ZODB.DB(fs, cache_size=1600)
        self.conn = self.zdb.open()
        root = self.conn.root()
        if 'rdflib' not in root:
            store = plugin.get('ZODB', Store)()
            root['rdflib'] = store
        try:
            transaction.commit()
        except Exception:
            # catch commit exception and close db.
            # otherwise db would stay open and follow up tests
            # will detect the db in error state
            L.exception('Forced to abort transaction on ZODB store opening', exc_info=True)
            transaction.abort()
        transaction.begin()
        self.graph = ConjunctiveGraph(root['rdflib'])
        self.graph.open(openstr)

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
            L.warning('Forced to abort transaction on ZODB store closing', exc_info=True)
            transaction.abort()
        self.conn.close()
        self.zdb.close()
        self.graph = False


class SQLSource(RDFSource):

    def __init__(self, *args, **kwargs):
        super(SQLSource, self).__init__(*args, **kwargs)
        self.conf['rdf.store'] = self.store_name

    def open(self):
        try:
            from rdflib_sqlalchemy import registerplugins
            from sqlalchemy import event
        except ImportError:
            raise OpenFailError('The rdflib-sqlalchemy package is not installed.'
                    ' You may need to install one of "sqlite_source", "mysql_source", or'
                    ' "postgresql_source" extra for owmeta.'
                    ' For example, change "owmeta" in your setup.py or'
                    ' requirements.txt to "owmeta[sqlite_source]" and reinstall')
        registerplugins()

        store = plugin.get("SQLAlchemy", Store)(**self._initargs())
        self.graph = ConjunctiveGraph(store)
        cfg = self._openconfig()
        self.graph.open(cfg, create=True)

    def _initargs(self):
        a = self._initargs_augment()
        if not a or not isinstance(a, dict):
            return dict()
        return a

    def _openconfig(self):
        c = self.conf['rdf.store_conf']
        if isinstance(c, dict):
            c = dict(c)
            url = c.pop('url', None)
            if not url:
                raise OpenFailError('A "url" argument must be provided in config dict')
            c.pop('init_args', None)
            self.url = self._openurl(url)
            c['url'] = self.url
            return c
        else:
            self.url = self._openurl(c)
            return self.url

    def _openurl(self, url):
        return url

    def _initargs_augment(self):
        c = self.conf['rdf.store_conf']
        if isinstance(c, dict):
            initargs = self.conf['rdf.store_conf'].get('init_args', None)
            if initargs:
                return dict(initargs)


class SQLiteSource(SQLSource):
    store_name = 'sqlite'

    def _openurl(self, url):
        return 'sqlite:///' + url


class MySQLSource(SQLSource):
    store_name = 'mysql'


class PostgreSQLSource(SQLSource):
    store_name = 'postgresql'
