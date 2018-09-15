from __future__ import print_function
import sys
import os
from os.path import exists, abspath, join as pth_join, dirname, isabs, relpath, normpath
from os import makedirs, mkdir, listdir
from contextlib import contextmanager
import hashlib
import shutil
import json
import logging
import errno
try:
    from tempfile import TemporaryDirectory
except ImportError:
    from backports.tempfile import TemporaryDirectory

from .command_util import IVar, SubCommand
from .context import Context


L = logging.getLogger(__name__)

DATA_CONTEXT_KEY = 'data_context_id'
IMPORTS_CONTEXT_KEY = 'imports_context_id'
DEFAULT_SAVE_CALLABLE_NAME = 'pow_data'


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
        from PyOpenWorm.datasource import DataSource
        conf = self._parent._conf()
        ctx = self._parent._data_ctx()
        dt = ctx.stored(DataSource)(conf=conf)
        nm = conf['rdf.graph'].namespace_manager
        for x in dt.load():
            yield nm.normalizeUri(x.identifier)

    def show(self, data_source):
        '''
        Parameters
        ----------
        data_source : str
            The ID of the data source to show
        '''
        from PyOpenWorm.datasource import DataSource

        uri = self._parent._den3(data_source)
        for x in self._parent._data_ctx.stored(DataSource)(ident=uri).load():
            self._parent.message(x.format_str(stored=True))

    def list_kinds(self):
        """
        List kinds of sources
        """


class POWTranslator(object):
    def __init__(self, parent):
        self._parent = parent

    def list(self, context=None):
        '''
        List translator types
        '''
        from PyOpenWorm.datasource import DataTranslator
        conf = self._parent._conf()
        dt = self._parent._data_ctx.stored(DataTranslator)(conf=conf)
        nm = conf['rdf.graph'].namespace_manager
        for x in dt.load():
            yield nm.normalizeUri(x.identifier)

    def show(self, translator):
        '''
        Show a translator

        Parameters
        ----------
        translator : str
            The translator to show
        '''
        from PyOpenWorm.datasource import DataTranslator
        conf = self._parent._conf()
        uri = self._parent._den3(translator)
        dt = self._parent._data_ctx.stored(DataTranslator)(ident=uri, conf=conf)
        for x in dt.load():
            self._parent.message(x)
            return


class POWNamespace(object):
    def __init__(self, parent):
        self._parent = parent

    def list(self):
        conf = self._parent._conf()
        nm = conf['rdf.graph'].namespace_manager
        for prefix, uri in nm.namespaces():
            self._parent.message(prefix, uri.n3())


class _ProgressMock(object):

    def __getattr__(self, name):
        return type(self)()

    def __call__(self, *args, **kwargs):
        return type(self)()


class POWConfig(object):
    user = IVar(value_type=bool,
                default_value=False,
                doc='If set, configs are only for the user; otherwise, they \
                       would be committed to the repository')

    def __init__(self, parent):
        self._parent = parent

    def __setattr__(self, t, v):
        super(POWConfig, self).__setattr__(t, v)

    @IVar.property('user.conf', value_type=str)
    def user_config_file(self):
        ''' The user config file name '''
        if isabs(self._user_config_file):
            return self._user_config_file
        return pth_join(self._parent.powdir, self._user_config_file)

    @user_config_file.setter
    def user_config_file(self, val):
        self._user_config_file = val

    def _get_config_file(self):
        if not exists(self._parent.powdir):
            raise POWDirMissingException(self._parent.powdir)

        if self.user:
            res = self.user_config_file
        else:
            res = self._parent.config_file

        if not exists(res):
            if self.user:
                self._init_user_config_file()
            else:
                self._parent._init_config_file()
        return res

    def _init_user_config_file(self):
        with open(self.user_config_file, 'w') as f:
            write_config({}, f)

    def get(self, key):
        '''
        Read a config value

        Parameters
        ----------
        key : str
            The configuration key
        '''
        fname = self._get_config_file()
        with open(fname, 'r') as f:
            ob = json.load(f)
            return ob.get(key)

    def set(self, key, value):
        '''
        Set a config value

        Parameters
        ----------
        key : str
            The configuration key
        value : str
            The value to set
        '''
        fname = self._get_config_file()
        with open(fname, 'r+') as f:
            ob = json.load(f)
            f.seek(0)
            try:
                json_value = json.loads(value)
            except json.decoder.JSONDecodeError:
                json_value = value
            ob[key] = json_value
            write_config(ob, f)

    def delete(self, key):
        '''
        Deletes a config value

        Parameters
        ----------
        key : str
            The configuration key
        '''
        fname = self._get_config_file()
        with open(fname, 'r+') as f:
            ob = json.load(f)
            f.seek(0)
            del ob[key]
            write_config(ob, f)


_PROGRESS_MOCK = _ProgressMock()


@contextmanager
def default_progress_reporter(*args, **kwargs):
    yield _PROGRESS_MOCK


class POW(object):
    """
    High-level commands for working with PyOpenWorm data
    """

    graph_accessor_finder = IVar(doc='Finds an RDFLib graph from the given URL')

    basedir = IVar('.', doc='The base directory. powdir is resolved against this base')

    repository_provider = IVar(doc='The provider of the repository logic'
                                   ' (cloning, initializing, committing, checkouts)')

    # N.B.: Sub-commands are created on-demand when you access the attribute,
    # hence they do not, in any way, store attributes set on them. You must
    # save the instance of the subcommand to a variable in order to make
    # multiple statements including that sub-command
    config = SubCommand(POWConfig)

    source = SubCommand(POWSource)

    translator = SubCommand(POWTranslator)

    namespace = SubCommand(POWNamespace)

    def __init__(self):
        self.progress_reporter = default_progress_reporter
        self.message = lambda *args, **kwargs: print(*args, **kwargs)

    @IVar.property('.pow')
    def powdir(self):
        '''
        The base directory for PyOpenWorm files. The repository provider's files also go under here
        '''
        if isabs(self._powdir):
            return self._powdir
        return pth_join(self.basedir, self._powdir)

    @powdir.setter
    def powdir(self, val):
        self._powdir = val

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

    @IVar.property
    def log_level(self):
        '''
        Log level
        '''
        return logging.getLevelName(logging.getLogger().getEffectiveLevel())

    @log_level.setter
    def log_level(self, level):
        logging.basicConfig()
        logging.getLogger().setLevel(getattr(logging, level))
        logging.getLogger('PyOpenWorm.mapper').setLevel(logging.ERROR)
        # Tailoring for known loggers

    def save(self, module, provider=None, context=None):
        '''
        Save the data in the given context

        Parameters
        ----------
        module : str
            Name of the module housing the provider
        provider : str
            Name of the provider, a callble that accepts a context object and adds statements to it. Can be a "dotted"
            name indicating attribute accesses
        context : str
            The target context
        '''
        import importlib as IM
        conf = self._conf()
        if not context:
            ctx = _POWSaveContext(self._data_ctx)
        else:
            ctx = _POWSaveContext(Context(ident=context, conf=conf))

        m = IM.import_module(module)
        print(m)
        if not provider:
            provider = DEFAULT_SAVE_CALLABLE_NAME
        attr_chain = provider.split('.')
        p = m
        for x in attr_chain:
            p = getattr(p, x)
        print(p)
        p(ctx)
        # validation of imports
        ctx.save_context(graph=conf['rdf.graph'])

    def context(self, context=None, user=False):
        '''
        Read or set current target context for the repository

        Parameters
        ----------
        context : str
            The context to set
        user : bool
            If set, set the context only for the current user. Has no effect for retrieving the context
        '''
        if context is not None:
            config = self.config
            config.user = user
            config.set(DATA_CONTEXT_KEY, context)
        else:
            return self._conf().get(DATA_CONTEXT_KEY)

    def imports_context(self, context=None, user=False):
        '''
        Read or set current target imports context for the repository

        Parameters
        ----------
        context : str
            The context to set
        user : bool
            If set, set the context only for the current user. Has no effect for retrieving the context
        '''
        if context is not None:
            config = self.config
            config.user = user
            config.set(IMPORTS_CONTEXT_KEY, context)
        else:
            return self._conf().get(IMPORTS_CONTEXT_KEY)

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
        try:
            self._ensure_powdir()
            if not exists(self.config_file):
                self._init_config_file()
            elif update_existing_config:
                with open(self.config_file, 'r+') as f:
                    conf = json.load(f)
                    conf['rdf.store_conf'] = relpath(abspath(self.store_name),
                                                     abspath(self.basedir))
                    f.seek(0)
                    write_config(conf, f)

            self._init_store()
            self._init_repository()
        except Exception as e:
            self._ensure_no_powdir()
            raise e

    def _ensure_no_powdir(self):
        if exists(self.powdir):
            shutil.rmtree(self.powdir)

    def _init_config_file(self):
        with open(self._default_config(), 'r') as f:
            default = json.load(f)
            with open(self.config_file, 'w') as of:
                default['rdf.store_conf'] = relpath(abspath(self.store_name),
                                                    abspath(self.basedir))
                write_config(default, of)

    def _init_repository(self):
        if self.repository_provider is not None:
            self.repository_provider.init(base=self.powdir)

    def _den3(self, s):
        from rdflib.namespace import is_ncname
        from rdflib.term import URIRef
        conf = self._conf()
        nm = conf['rdf.graph'].namespace_manager
        s = s.strip('<>')
        parts = s.split(':')
        if len(parts) > 1 and is_ncname(parts[1]):
            for pref, ns in nm.namespaces():
                if pref == parts[0]:
                    s = URIRef(ns + parts[1])
                    break
        return URIRef(s)

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
        if not dat or self._dat_file != self.config_file:
            if not exists(self.config_file):
                raise NoConfigFileError(self.config_file)

            with open(self.config_file) as repo_config:
                rc = json.load(repo_config)
            if not exists(self.config.user_config_file):
                uc = {}
            else:
                with open(self.config.user_config_file) as user_config:
                    uc = json.load(user_config)

            rc.update(uc)
            store_conf = rc.get('rdf.store_conf', None)
            if store_conf and isinstance(store_conf, str) and not isabs(store_conf):
                rc['rdf.store_conf'] = abspath(pth_join(self.basedir, store_conf))
            dat = Data.process_config(rc)
            dat.init_database()
            self._dat = dat
            self._dat_file = self.config_file
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
        try:
            makedirs(self.powdir)
            self.message('Cloning...', file=sys.stderr)
            with self.progress_reporter(file=sys.stderr, unit=' objects', miniters=0) as progress:
                self.repository_provider.clone(url, base=self.powdir, progress=progress)
            if not exists(self.config_file):
                self._init_config_file()
            self._init_store()
            self.message('Deserializing...', file=sys.stderr)
            with self.progress_reporter(unit=' ctx', file=sys.stderr) as ctx_prog, \
                    self.progress_reporter(unit=' triples', file=sys.stderr, leave=False) as trip_prog:
                self._load_all_graphs(ctx_prog, trip_prog)
            self.message('Done!', file=sys.stderr)
        except BaseException as e:
            self._ensure_no_powdir()
            raise e

    def _load_all_graphs(self, progress, trip_prog):
        import transaction
        from rdflib import plugin
        from rdflib.parser import Parser, create_input_source
        idx_fname = pth_join(self.powdir, 'graphs', 'index')
        triples_read = 0
        if exists(idx_fname):
            dest = self._conf()['rdf.graph']
            with open(idx_fname) as index_file:
                cnt = 0
                for l in index_file:
                    cnt += 1
                index_file.seek(0)
                progress.total = cnt
                with transaction.manager:
                    for l in index_file:
                        fname, ctx = l.strip().split(' ')
                        parser = plugin.get('nt', Parser)()
                        with open(pth_join(self.powdir, 'graphs', fname), 'rb') as f, \
                                _BatchAddGraph(dest.get_context(ctx), batchsize=4000) as g:
                            parser.parse(create_input_source(f), g)
                        progress.update(1)
                        triples_read += g.count
                        trip_prog.update(g.count)
                    progress.write('Finalizing writes to database...')
        progress.write('Loaded {:,} triples'.format(triples_read))

    def translate(self, translator, imports_context_ident, output_key=None, translation_directory=None,
                  data_sources=(), named_data_sources=None):
        """
        Do a translation with the named translator and inputs

        Parameters
        ----------
        translator : str
            Translator identifier
        imports_context_ident : str
            Identifier for the imports context. All imports go in here
        output_key : str
            Output identifier
        translation_directory : str
            Directory holding files used in the translation, if needed
        data_sources : list of str
            Input data sources
        named_data_sources : dict
            Named input data sources
        """
        if named_data_sources is None:
            named_data_sources = dict()
        imports_context = Context(ident=imports_context_ident, conf=self._conf())
        translator_obj = self._lookup_translator(translator)
        if translator_obj is None:
            raise GenericUserError('No translator for ' + translator)

        graph = self._rdf
        positional_sources = [self._lookup_source(src) for src in data_sources]
        if None in positional_sources:
            raise GenericUserError('No source for ' + data_sources[positional_sources.index(None)])
        named_sources = {k: self._lookup_source(src) for k, src in named_data_sources}
        saved_contexts = set([])
        with TemporaryDirectory(prefix='pow-translate.') as d:
            orig_wd = os.getcwd()
            os.chdir(d)
            try:
                if translation_directory:
                    self._stage_translation_directory(normpath(pth_join(orig_wd, translation_directory)), d)
                res = translator_obj(*positional_sources, output_key=output_key, **named_sources)
                res.data_context.save_context(inline_imports=True, graph=graph, saved_contexts=saved_contexts)
                res.data_context.save_imports(imports_context, graph=graph)
                res.evidence_context.save_context(inline_imports=True, graph=graph, saved_contexts=saved_contexts)
                res.evidence_context.save_imports(imports_context, graph=graph)
            finally:
                os.chdir(orig_wd)

    def _stage_translation_directory(self, source_directory, target_directory):
        self.message('Copying files into {} from {}'.format(target_directory, source_directory))
        # TODO: Add support for a selector based on a MANIFEST and/or ignore
        # file to pass in as the 'ignore' option to copytree
        for dirent in listdir(source_directory):
            src = pth_join(source_directory, dirent)
            dst = pth_join(target_directory, dirent)
            self.message('Copying {} to {}'.format(src, dst))
            try:
                shutil.copytree(src, dst)
            except OSError as e:
                if e.errno == errno.ENOTDIR:
                    shutil.copy2(src, dst)

    def _lookup_translator(self, tname):
        from PyOpenWorm.datasource import DataTranslator
        for x in self._data_ctx.stored(DataTranslator)(ident=tname).load():
            return x

    def _lookup_source(self, sname):
        from PyOpenWorm.datasource import DataSource
        for x in self._data_ctx.stored(DataSource)(ident=sname).load():
            return x

    @property
    def _data_ctx(self):
        conf = self._conf()
        try:
            return Context(ident=conf[DATA_CONTEXT_KEY], conf=conf)
        except KeyError:
            raise ConfigMissingException(DATA_CONTEXT_KEY)

    def reconstitute(self, data_source):
        '''
        Recreate a data source by executing the chain of translators that went into making it.

        Parameters
        ----------
        data_source : str
            Identifier for the data source to reconstitute
        '''

    def serialize(self, destination, format='nquads'):
        '''
        Serialize the graph to a file

        Parameters
        ----------
        destination : file or str
            A file-like object to write the file to or a file name
        format : str
            Serialization format (ex, 'n3', 'nquads')
        '''
        self._conf()['rdf.graph'].serialize(destination, format=format)

    def _package_path(self):
        """
        Get the package path
        """
        from pkgutil import get_loader
        return dirname(get_loader('PyOpenWorm').get_filename())

    def _default_config(self):
        return pth_join(self._package_path(), 'default.conf')

    def list_contexts(self):
        '''
        List contexts
        '''
        for c in self._conf()['rdf.graph'].contexts():
            yield c.identifier

    @property
    def _rdf(self):
        return self._conf()['rdf.graph']

    def commit(self, message):
        '''
        Write the graph to the local repository

        Parameters
        ----------
        message : str
            commit message
        '''
        repo = self.repository_provider
        self._serialize_graphs()
        repo.commit(message)

    def _serialize_graphs(self):
        from rdflib import plugin
        from rdflib.serializer import Serializer
        g = self._conf()['rdf.graph']
        repo = self.repository_provider

        repo.base = self.powdir
        graphs_base = pth_join(self.powdir, 'graphs')

        if repo.is_dirty:
            repo.reset()

        if exists(graphs_base):
            repo.remove(['graphs'], recursive=True)
            shutil.rmtree(graphs_base)

        mkdir(graphs_base)
        files = []
        ctx_data = []
        for x in g.contexts():
            ident = x.identifier
            hs = hashlib.sha256(ident.encode()).hexdigest()
            fname = pth_join(graphs_base, hs + '.nt')
            i = 1
            while exists(fname):
                fname = pth_join(graphs_base, hs + '-' + i + '.nt')
                i += 1
            files.append(fname)
            serializer = plugin.get('nt', Serializer)(sorted(x))
            with open(fname, 'wb') as gfile:
                serializer.serialize(gfile)
            ctx_data.append((relpath(fname, graphs_base), ident))

        index_fname = pth_join(graphs_base, 'index')
        with open(index_fname, 'w') as index_file:
            for l in sorted(ctx_data):
                print(*l, file=index_file)

        files.append(index_fname)
        repo.add([relpath(f, self.powdir) for f in files] + [relpath(self.config_file, self.powdir),
                                                             'graphs'])

    def diff(self):
        """
        """
        self._serialize_graphs()

    def merge(self):
        """
        """

    def push(self):
        """
        """

    def tag(self):
        """
        """


class _POWSaveContext(Context):

    def __init__(self, backer):
        self._backer = backer  #: Backing context
        self._ctxids = set([self._backer.identifier])
        self._unvalidated_statements = []

    def add_import(self, ctx):
        self._ctxids.add(ctx.identifier)
        return self._backer.add_import(ctx)

    def add_statement(self, stmt):
        if not all(x in self._ctxids for x in
                   (stmt.object.context.identifier,
                    stmt.property.context.identifier,
                    stmt.object.property.identifier)):
            self._unvalidated_statements.append(stmt)
        return self._backer.add_statement(stmt)

    def __getattr__(self, name):
        return getattr(self._backer, name)

    def save_context(self, *args, **kwargs):
        if self._unvalidated_statements:
            raise StatementValidationError(list(self._unvalidated_statements))
        return self._backer.save_context(*args, **kwargs)


class _BatchAddGraph(object):
    ''' Wrapper around graph that turns calls to 'add' into calls to 'addN' '''
    def __init__(self, graph, batchsize=1000, *args, **kwargs):
        self.graph = graph
        self.g = (graph,)
        self.batchsize = batchsize
        self.reset()

    def reset(self):
        self.batch = []
        self.count = 0

    def add(self, triple):
        if self.count > 0 and self.count % self.batchsize == 0:
            self.graph.addN(self.batch)
            self.batch = []
        self.count += 1
        self.batch.append(triple + self.g)

    def __enter__(self):
        self.reset()
        return self

    def __exit__(self, *exc):
        if exc[0] is None:
            self.graph.addN(self.batch)


def write_config(ob, f):
    json.dump(ob, f, sort_keys=True, indent=4, separators=(',', ': '))
    f.write('\n')
    f.truncate()


class GenericUserError(Exception):
    ''' An error which should be reported to the user. Not necessarily an error that is the user's fault '''


class InvalidGraphException(GenericUserError):
    ''' Thrown when a graph cannot be translated due to formatting errors '''


class UnreadableGraphException(GenericUserError):
    ''' Thrown when a graph cannot be read due to it being missing, the active user lacking permissions, etc. '''


class NoConfigFileError(GenericUserError):
    pass


class POWDirMissingException(GenericUserError):
    pass


class StatementValidationError(GenericUserError):
    pass


class ConfigMissingException(GenericUserError):
    def __init__(self, key):
        self.key = key
