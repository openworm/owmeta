from __future__ import print_function
from os.path import exists, abspath, join as pth_join, dirname, isabs, relpath
from os import makedirs, mkdir
import hashlib
import shutil
import json
import logging

from .command_util import IVar, SubCommand


L = logging.getLogger(__name__)


class POWSource(object):
    ''' Commands for working with DataSource objects '''

    def __init__(self, parent):
        self._parent = parent

    # Commands specific to sources
    def create(self, kind, key, *args, **kwargs):
        """
        Create the source and add it to the graph.

        Arguments are determined by the type of the data source

        Parameters
        ----------
        kind : rdflib.term.URIRef
            The kind of source to create
        key : str
            The key, a unique name for the source
        """

    def list(self, context=None):
        """
        List known sources
        """

    def list_kinds(self):
        """
        List kinds of sources
        """


class POW(object):
    """
    High-level commands for working with PyOpenWorm data
    """

    graph_accessor_finder = IVar(doc='Finds an RDFLib graph from the given URL')

    powdir = IVar('.pow',
                  doc='The base directory for PyOpenWorm files.'
                      ' The repository provider\'s files also go under here')

    repository_proivder = IVar(doc='The provider of the repository logic'
                                   ' (cloning, initializing, committing, checkouts)')

    source = SubCommand(POWSource)

    @IVar.property('pow.conf', value_type=str)
    def config_file(self):
        ''' The config file name '''
        if isabs(self._config_file):
            return self._config_file
        return pth_join(self.powdir, self._config_file)

    @config_file.setter
    def config_file(self, val):
        self._config_file = val

    @IVar.property('worm.db')
    def store_name(self):
        ''' The file name of the database store '''
        if isabs(self._store_name):
            return self._store_name
        return pth_join(self.powdir, self._store_name)

    @store_name.setter
    def store_name(self, val):
        self._store_name = val

    def _ensure_powdir(self):
        if not exists(self.powdir):
            makedirs(self.powdir)

    def init(self, update_existing_config=False):
        """
        Makes a new graph store.

        The configuration file will be created if it does not exist. If it
        *does* exist, the location of the database store will, by default, not
        be changed in that file

        Parameters
        ----------
        update_existing_config : bool
            If True, updates the existing config file to point to the given
            file for the store configuration
        """
        self._ensure_powdir()
        store_fname = abspath(self.store_name)
        if not exists(self.config_file):
            with open(self._default_config(), 'r') as f:
                default = json.load(f)
                with open(self.config_file, 'w') as of:
                    default['rdf.store_conf'] = store_fname
                    self._write_config(default, of)
        elif update_existing_config:
            with open(self.config_file, 'r+') as f:
                conf = json.load(f)
                conf['rdf.store_conf'] = store_fname
                f.seek(0)
                self._write_config(conf, f)

        self._init_store()
        self._init_repository()

    def _write_config(self, conf, dest):
        json.dump(conf, dest, sort_keys=True, indent=4, separators=(',', ': '))
        dest.write('\n')

    def _init_repository(self):
        if self.repository_proivder is not None:
            self.repository_proivder.init(base=self.powdir)

    def fetch_graph(self, url):
        """
        Fetch a graph

        Parameters
        ----------
        url : str
            URL for the graph
        """
        res = self._obtain_graph_accessor(url)
        if not res:
            raise UnreadableGraphException('Could not read the graph at {}'.format(url))
        return res()

    def add_graph(self, url=None, context=None, include_imports=True):
        """
        Fetch a graph and add it to the local store.

        Parameters
        ----------
        url : str
            The URL of the graph to fetch
        context : rdflib.term.URIRef
            If provided, only this context and, optionally, its imported graphs
            will be added.
        include_imports : bool
            If True, imports of the named context will be included. Has no
            effect if context is None.
        """
        graph = self.fetch_graph(url)
        dat = self._conf()

        dat['rdf.graph'].addN(graph.quads((None, None, None, context)))

    def _obtain_graph_accessor(self, url):
        if self.graph_accessor_finder is None:
            raise Exception('No graph_accessor_finder has been configured')

        return self.graph_accessor_finder(url)

    def _conf(self):
        from PyOpenWorm.data import Data
        dat = getattr(self, '_dat', None)
        if not dat:
            dat = Data.open(self.config_file)
            dat.init_database()
            self._dat = dat
        return dat

    _init_store = _conf

    def clone(self, url=None, update_existing_config=False):
        """Clone a data store

        Parameters
        ----------
        url : str
            URL of the data store to clone
        update_existing_config : bool
            If True, updates the existing config file to point to the given
            file for the store configuration
        """
        # TODO: As a first cut
        # 1) should download a file at the given URL
        #
        # 2) verify that it's an RDF graph
        #
        # 3) init a git repo
        #
        # 4) rewrite the serialization as an nquads (setting the clone url as
        # the default context)
        #
        # 5) add the nquads serialization to the git repo
        #
        # 6) commit to the git repo
        #
        # 7) do a similar thing to POW::init for initializing the database
        #
        # 8) add the contents of the nquads to the new database
        #
        # 9) and, finally, print some summary stats about the newly created
        # database like how many triples, contexts, total size downloaded, etc.

    def translate(self, translator, output_key=None, *data_sources, **named_data_sources):
        """
        Do a translation with the named translator and inputs

        Parameters
        ----------
        translator : str
            Translator identifier
        output_key : str
            Output identifier
        *data_sources : str
            Input data sources
        **named_data_sources : str
            Named input data sources
        """

    def reconstitute(self, data_source):
        """
        Recreate a data source by executing the chain of translators that went into making it.

        Parameters
        ----------
        data_source : str
            Identifier for the data source to reconstitute
        """

    def _package_path(self):
        """
        Get the package path
        """
        from pkgutil import get_loader
        return dirname(get_loader('PyOpenWorm').get_filename())

    def _default_config(self):
        return pth_join(self._package_path(), 'default.conf')

    def commit(self):
        """
        Write the graph to the local repository
        """
        from rdflib import plugin
        from rdflib.serializer import Serializer
        g = self._conf()['rdf.graph']

        graphs_base = pth_join(self.powdir, 'graphs')
        if exists(graphs_base):
            shutil.rmtree(graphs_base)

        mkdir(graphs_base)
        ctx_data = []
        for x in g.contexts():
            ident = x.identifier
            hs = hashlib.sha256(ident.encode()).hexdigest()
            fname = pth_join(graphs_base, hs + '.nt')
            i = 1
            while exists(fname):
                fname = pth_join(graphs_base, hs + '-' + i + '.nt')
                i += 1
            ctx_data.append((hs, relpath(fname, graphs_base), ident))
            serializer = plugin.get('nt', Serializer)(sorted(x))
            with open(fname, 'wb') as gfile:
                serializer.serialize(gfile)
        with open(pth_join(graphs_base, '.index'), 'w') as index_file:
            for l in sorted(ctx_data):
                print(*l, file=index_file)

    def diff(self):
        """
        """

    def merge(self):
        """
        """

    def push(self):
        """
        """

    def tag(self):
        """
        """


class UnreadableGraphException(Exception):
    pass


class InvalidGraphException(Exception):
    pass
