from __future__ import print_function, absolute_import
import sys
import os
from os.path import exists, abspath, join as pth_join, dirname, isabs, relpath
from os import makedirs, mkdir, listdir, rename, unlink, stat

from contextlib import contextmanager
try:
    from os import scandir
except ImportError:
    from scandir import scandir as _scandir

    @contextmanager
    def scandir(directory):
        sd = _scandir(directory)
        try:
            yield sd
        finally:
            del sd

import hashlib
import shutil
import json
import logging
import errno
from collections import namedtuple
from six import string_types

try:
    from tempfile import TemporaryDirectory
except ImportError:
    from backports.tempfile import TemporaryDirectory

from .command_util import IVar, SubCommand, GeneratorWithData
from .context import Context, DATA_CONTEXT_KEY, IMPORTS_CONTEXT_KEY
from .capability import provide, is_capable
from .capabilities import FilePathProvider
from .datasource_loader import DataSourceDirLoader, LoadFailed


L = logging.getLogger(__name__)

DEFAULT_SAVE_CALLABLE_NAME = 'pow_data'


class POWSourceData(object):
    ''' Commands for saving and loading data for DataSources '''
    def __init__(self, parent):
        self._source_command = parent
        self._pow_command = parent._parent

    def retrieve(self, source, archive='data.tar', archive_type=None):
        '''
        Retrieves the data for the source

        Parameters
        ----------
        source : str
            The source for data
        archive : str
            The file name of the archive. If this ends with an extension like
            '.zip', and no `archive_type` argument is given, then an archive
            will be created of that type. The archive name will *not* have any
            extension appended in any case.
        archive_type : str
            The type of the archive to create.
        '''
        from PyOpenWorm.datasource import DataSource
        sid = self._pow_command._den3(source)
        if not archive_type:
            for ext in EXT_TO_ARCHIVE_FMT:
                if archive.endswith(ext):
                    archive_type = EXT_TO_ARCHIVE_FMT.get(ext)
                    break

        if not archive_type:
            if ext:
                msg = "The extension '{}', does not match any known archive format." \
                        " Defaulting to TAR format"
                L.warning(msg.format(ext))
            archive_type = 'tar'

        try:
            sources = self._pow_command._data_ctx.stored(DataSource)(ident=sid).load()
            for data_source in sources:
                dd = self._pow_command._dsd[data_source]
        except KeyError:
            raise GenericUserError('Could not find data for {} ({})'.format(sid, source))

        with self._pow_command._tempdir(prefix='pow-source-data-retrieve.') as d:
            temp_archive = shutil.make_archive(pth_join(d, 'archive'), archive_type, dd)
            rename(temp_archive, archive)


EXT_TO_ARCHIVE_FMT = {
    '.tar.bz2': 'bztar',
    '.tar.gz': 'gztar',
    '.tar.xz': 'xztar',
    '.tar': 'tar',
    '.zip': 'zip',
}


class POWSource(object):
    ''' Commands for working with DataSource objects '''

    data = SubCommand(POWSourceData)

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

    def list(self, context=None, kind=None, full=False):
        """
        List known sources

        Parameters
        ----------
        kind : str
            Only list sources of this kind
        context : str
            The context to query for sources
        full : bool
            Whether to (attempt to) shorten the source URIs by using the namespace manager
        """
        from .datasource import DataSource
        conf = self._parent._conf()
        if context is not None:
            ctx = self._make_ctx(context)
        else:
            ctx = self._parent._data_ctx
        if kind is None:
            kind = DataSource.rdf_type
        kind_uri = self._parent._den3(kind)

        dst = ctx.stored(ctx.stored.resolve_class(kind_uri))
        dt = dst.query(conf=conf)
        nm = conf['rdf.graph'].namespace_manager

        def format_id(r):
            if full:
                return r.identifier
            return nm.normalizeUri(r.identifier)

        def format_comment(r):
            comment = r.rdfs_comment()
            if comment:
                return '\n'.join(comment)
            return ''

        return GeneratorWithData(dt.load(),
                                 text_format=format_id,
                                 default_columns=('ID',),
                                 columns=(format_id,
                                          format_comment),
                                 header=('ID', 'Comment'))

    def show(self, *data_source):
        '''
        Parameters
        ----------
        *data_source : str
            The ID of the data source to show
        '''
        from PyOpenWorm.datasource import DataSource

        for ds in data_source:
            uri = self._parent._den3(ds)
            for x in self._parent._data_ctx.stored(DataSource)(ident=uri).load():
                self._parent.message(x.format_str(stored=True))

    def list_kinds(self, full=False):
        """
        List kinds of sources

        Parameters
        ----------
        full : bool
            Whether to (attempt to) shorten the source URIs by using the namespace manager
        """
        from .datasource import DataSource
        from .dataObject import TypeDataObject, RDFSSubClassOfProperty
        from yarom.graphObject import ZeroOrMoreTQLayer
        from .rdf_query_util import zomifier
        conf = self._parent._conf()
        ctx = self._parent._data_ctx
        rdfto = ctx.stored(DataSource.rdf_type_object)
        sc = ctx.stored(TypeDataObject)()
        sc.attach_property(RDFSSubClassOfProperty)
        sc.rdfs_subclassof_property(rdfto)
        nm = conf['rdf.graph'].namespace_manager
        g = ZeroOrMoreTQLayer(zomifier(DataSource.rdf_type), ctx.stored.rdf_graph())
        for x in sc.load(graph=g):
            if full:
                yield x.identifier
            else:
                yield nm.normalizeUri(x.identifier)


class POWTranslator(object):
    def __init__(self, parent):
        self._parent = parent

    def list(self, context=None, full=False):
        '''
        List translators

        Parameters
        ----------
        context : str
            The root context to search
        full : bool
            Whether to (attempt to) shorten the source URIs by using the namespace manager
        '''
        from PyOpenWorm.datasource import DataTranslator
        conf = self._parent._conf()
        if context is not None:
            ctx = self._make_ctx(context)
        else:
            ctx = self._parent._data_ctx
        dt = ctx.stored(DataTranslator)(conf=conf)
        nm = conf['rdf.graph'].namespace_manager
        for x in dt.load():
            if full:
                yield x.identifier
            else:
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


class POWDist(object):
    def __init__(self, parent):
        self._parent = parent


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
            except ValueError:
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


POSSIBLE_EDITORS = [
    '/usr/bin/vi',
    '/usr/bin/vim',
    '/usr/bin/nano',
    'vim',
    'vi',
    'nano'
]


class POWEvidence(object):
    def __init__(self, parent):
        self._parent = parent

    def get(self, identifier, rdf_type=None):
        '''
        Retrieves evidence for the given object. If there are multiple types for the object, the evidence for only one
        type will be shown, but you can specify which type should be used.

        Parameters
        ----------
        identifier : str
            The object to show evidence for
        rdf_type : str
            Type of the object to show evidence
        '''
        from PyOpenWorm.evidence import Evidence
        from PyOpenWorm.data_trans.data_with_evidence_ds import DataWithEvidenceDataSource
        from PyOpenWorm.contextDataObject import ContextDataObject
        ctx = self._parent._data_ctx.stored
        identifier = self._parent._den3(identifier)
        rdf_type = self._parent._den3(rdf_type)
        if rdf_type:
            base_type = ctx(ctx.resolve_class(rdf_type))
        else:
            from PyOpenWorm.dataObject import DataObject
            base_type = ctx(DataObject)

        q = base_type.query(ident=identifier)
        for l in q.load():
            if isinstance(l, ContextDataObject):
                evq = ctx(Evidence).query()
                evq.supports(l)
                self._message_evidence(evq)
            if isinstance(l, DataWithEvidenceDataSource):
                evq = l.evidence_context.stored(Evidence).query()
                self._message_evidence(evq)

    def _message_evidence(self, evq):
        from PyOpenWorm.website import Website
        from PyOpenWorm.document import Document
        msg = self._parent.message
        for m in evq.load():
            ref = m.reference()
            if isinstance(ref, Document):
                msg(ref)
                titles = ['Author:',
                          'Title: ',
                          'URI:   ',
                          'DOI:   ',
                          'PMID:  ',
                          'WBID:  ']
                vals = [ref.author(),
                        ref.title(),
                        ref.uri(),
                        ref.doi(),
                        ref.pmid(),
                        ref.wbid()]
                for title, v in zip(titles, vals):
                    if v:
                        msg(title, v)
                msg()
            elif isinstance(ref, Website):
                msg(ref)
                titles = ['Title: ',
                          'URL:   ']
                vals = [ref.title(),
                        ref.url()]
                for title, v in zip(titles, vals):
                    if v:
                        msg(title, v)
                msg()


class POWContexts(object):
    def __init__(self, parent):
        self._parent = parent

    def edit(self, context=None, format=None, editor=None, list_formats=False):
        '''
        Edit a provided context or the current data context.

        The file name of the serialization will be passed as the sole argument to the editor. If the editor argument is
        not provided, will use the EDITOR environment variable. If EDITOR is also not defined, will try a few known
        editors until one is found. The editor must write back to the file.

        Parameters
        ----------
        context : str
            The context to edit
        format : str
            Serialization format (ex, 'n3', 'nquads'). Default 'n3'
        editor : str
            The program which will be used to edit the context serialization.
        list_formats : bool
            List the formats available for editing
        '''

        from rdflib.plugin import plugins
        from rdflib.serializer import Serializer
        from rdflib.parser import Parser

        stores = set(x.name for x in plugins(kind=Serializer))
        parsers = set(x.name for x in plugins(kind=Parser))
        formats = stores & parsers

        if list_formats:
            return formats

        if not format:
            format = 'n3'

        if format not in formats:
            raise GenericUserError("Unsupported format: " + format)

        from subprocess import call
        if context is None:
            ctx = self._parent._data_ctx
            ctxid = self._parent._conf()[DATA_CONTEXT_KEY]
        else:
            ctx = Context(ident=context, conf=self._parent._conf())
            ctxid = context

        if not editor:
            editor = os.environ['EDITOR'].strip()

        if not editor:
            for editor in POSSIBLE_EDITORS:
                if hasattr(shutil, 'which'):
                    editor = shutil.which(editor)
                    if editor:
                        break
                elif os.access(editor, os.R_OK | os.X_OK):
                    break

        if not editor:
            raise GenericUserError("No known editor could be found")

        with self._parent._tempdir(prefix='pow-context-edit.') as d:
            from rdflib import plugin
            from rdflib.parser import Parser, create_input_source
            import transaction
            parser = plugin.get(format, Parser)()
            fname = pth_join(d, 'data')
            with transaction.manager:
                with open(fname, mode='wb') as destination:
                    ctx.own_stored.rdf_graph().serialize(destination, format=format)
                call([editor, fname])
                with open(fname, mode='rb') as source:
                    g = self._parent._rdf.get_context(ctxid)
                    g.remove((None, None, None))
                    parser.parse(create_input_source(source), g)

    def list(self):
        '''
        List the set of contexts in the graph
        '''
        for c in self._parent._conf()['rdf.graph'].contexts():
            yield c.identifier

    def list_changed(self):
        '''
        Return the set of contexts which differ from the serialization on disk
        '''
        return self._parent._changed_contexts_set()


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

    contexts = SubCommand(POWContexts)

    evidence = SubCommand(POWEvidence)

    def __init__(self):
        from time import time
        self.progress_reporter = default_progress_reporter
        self.message = lambda *args, **kwargs: print(*args, **kwargs)
        self._clock = time
        self._data_source_directories = None
        self._changed_contexts = None
        self._pow_connection = None

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
        ''' Log level '''
        return logging.getLevelName(logging.getLogger().getEffectiveLevel())

    @log_level.setter
    def log_level(self, level):
        logging.getLogger().setLevel(getattr(logging, level.upper()))
        # Tailoring for known loggers

        # Generally, too verbose for the user
        logging.getLogger('PyOpenWorm.mapper').setLevel(logging.ERROR)

    def save(self, module, provider=None, context=None):
        '''
        Save the data in the given context

        Saves the "mapped" classes declared in a module and saves the objects declared by
        the "provider" (see the argument's description)

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
        import transaction
        import importlib as IM
        from functools import wraps
        conf = self._conf()

        added_cwd = False
        cwd = os.getcwd()
        if cwd not in sys.path:
            sys.path.append(cwd)
            added_cwd = True
        try:
            m = IM.import_module(module)
            provider_not_set = provider is None
            if not provider:
                provider = DEFAULT_SAVE_CALLABLE_NAME

            if not context:
                ctx = _POWSaveContext(self._data_ctx, m)
            else:
                ctx = _POWSaveContext(Context(ident=context, conf=conf), m)
            attr_chain = provider.split('.')
            p = m
            for x in attr_chain:
                try:
                    p = getattr(p, x)
                except AttributeError:
                    if provider_not_set and getattr(m, '__yarom_mapped_classes__', None):
                        def p(*args, **kwargs):
                            pass
                        break
                    raise
            ns = POWSaveNamespace(context=ctx)

            mapped_classes = getattr(m, '__yarom_mapped_classes__', None)
            if mapped_classes:
                # It's a module with class definitions -- take each of the mapped
                # classes and add their contexts so they're saved properly...
                np = p

                @wraps(p)
                def save_classes(ns):
                    mapper = conf['mapper']
                    mapper.process_module(module, m)
                    for mapped_class in mapped_classes:
                        ns.include_context(mapped_class.definition_context)
                    np(ns)
                p = save_classes

            with transaction.manager:
                p(ns)
                ns.save(graph=conf['rdf.graph'])
            return ns.created_contexts()
        finally:
            if added_cwd:
                sys.path.remove(cwd)

    def say(self, subject, property, object):
        '''
        Make a statement

        Parameters
        ----------
        subject : str
            The object which you want to say something about
        property : str
            The type of statement to make
        object : str
            The other object you want to say something about
        '''
        from PyOpenWorm.dataObject import DataObject
        import transaction
        dctx = self._data_ctx
        query = dctx.stored(DataObject)(ident=self._den3(subject))
        with transaction.manager:
            for ob in query.load():
                getattr(dctx(ob), property)(object)
            dctx.save()

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
                    conf['rdf.store_conf'] = pth_join('$POW', relpath(abspath(self.store_name),
                                                                      abspath(self.powdir)))
                    f.seek(0)
                    write_config(conf, f)

            self._init_store()
            self._init_repository()
        except Exception:
            self._ensure_no_powdir()
            raise

    def _ensure_no_powdir(self):
        if exists(self.powdir):
            shutil.rmtree(self.powdir)

    def _init_config_file(self):
        with open(self._default_config(), 'r') as f:
            default = json.load(f)
            with open(self.config_file, 'w') as of:
                default['rdf.store_conf'] = pth_join('$POW', relpath(abspath(self.store_name),
                                                                     abspath(self.powdir)))
                write_config(default, of)

    def _init_repository(self):
        if self.repository_provider is not None:
            self.repository_provider.init(base=self.powdir)

    def _den3(self, s):
        if not s:
            return s
        from rdflib.namespace import is_ncname
        from rdflib.term import URIRef
        conf = self._conf()
        nm = conf['rdf.graph'].namespace_manager
        s = s.strip(u'<>')
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
        from PyOpenWorm import connect
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

            # Pre-process the user-config to resolve variables based on the user
            # config-file location
            uc['configure.file_location'] = self.config.user_config_file
            udat = Data.process_config(uc, variables={'POW': self.powdir})

            rc.update(udat.items())
            rc['configure.file_location'] = self.config_file
            dat = Data.process_config(rc, variables={'POW': self.powdir})
            store_conf = dat.get('rdf.store_conf', None)
            if not store_conf:
                raise GenericUserError('rdf.store_conf is not defined in either of the POW'
                ' configuration files at ' + self.config_file + ' or ' +
                self.config.user_config_file + ' POW repository may have been initialized'
                ' incorrectly')
            if isabs(store_conf) and \
                    not store_conf.startswith(abspath(self.powdir)):
                raise GenericUserError('rdf.store_conf must specify a path inside of ' +
                        self.powdir + ' but instead it is ' + store_conf)
            self._pow_connection = connect(conf=dat)

            dat.on_context_changed(self._context_changed_handler())

            self._dat = dat
            self._dat_file = self.config_file
        return dat

    def _disconnect(self):
        from PyOpenWorm import disconnect
        if self._pow_connection is not None:
            disconnect(self._pow_connection)

    _init_store = _conf

    def _context_changed_handler(self):
        def handler(event):
            from rdflib.term import URIRef
            self._context_changed_times[URIRef(event.context)] = self._clock()
        return handler

    @property
    def _context_changed_times(self):
        if self._changed_contexts is None:
            import ZODB
            from ZODB.FileStorage import FileStorage
            import BTrees
            ccfile = pth_join(self.powdir, 'changed_contexts')
            all_changed = False
            if not exists(ccfile):
                all_changed = True
            try:
                fs = FileStorage(ccfile)
            except IOError:
                L.exception("Failed to create a FileStorage")
                raise Exception("Failed to open", ccfile)

            _cc_zdb = ZODB.DB(fs, cache_size=1600)
            _cc_conn = _cc_zdb.open()
            root = _cc_conn.root()
            if 'ccmap' not in root:
                root['ccmap'] = BTrees.family32.OO.BTree()
            self._changed_contexts = root['ccmap']
        return self._changed_contexts

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
            self._regenerate_database()
            self.message('Done!', file=sys.stderr)
        except BaseException as e:
            self._ensure_no_powdir()
            raise e

    def git(self, *args):
        '''
        Runs git commmands in the .pow directory

        Parameters
        ----------
        *args
            arguments to git
        '''
        import shlex
        from subprocess import Popen, PIPE
        startdir = os.getcwd()
        os.chdir(self.powdir)
        try:
            with Popen(['git'] + list(args), stdout=PIPE) as p:
                self.message(p.stdout.read().decode('utf-8', 'ignore'))
        finally:
            os.chdir(startdir)

    def regendb(self):
        from glob import glob
        for g in glob(self.store_name + '*'):
            self.message('unlink', g)
            os.unlink(g)

        ccfile = pth_join(self.powdir, 'changed_contexts')
        for g in glob(ccfile + '*'):
            self.message('unlink', g)
            os.unlink(g)
        self._regenerate_database()

    def _regenerate_database(self):
        with self.progress_reporter(unit=' ctx', file=sys.stderr) as ctx_prog, \
                self.progress_reporter(unit=' triples', file=sys.stderr, leave=False) as trip_prog:
            self._load_all_graphs(ctx_prog, trip_prog)

    def _load_all_graphs(self, progress, trip_prog):
        import transaction
        from rdflib import plugin
        from rdflib.term import URIRef
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
                        graph_fname = pth_join(self.powdir, 'graphs', fname)
                        with open(graph_fname, 'rb') as f, \
                                _BatchAddGraph(dest.get_context(ctx), batchsize=4000) as g:
                            parser.parse(create_input_source(f), g)

                        progress.update(1)
                        triples_read += g.count
                        trip_prog.update(g.count)
                        self._context_changed_times[URIRef(ctx)] = stat(graph_fname).st_mtime
                    progress.write('Finalizing writes to database...')
        progress.write('Loaded {:,} triples'.format(triples_read))

    def _graphs_index(self):
        idx_fname = pth_join(self.powdir, 'graphs', 'index')
        if exists(idx_fname):
            with open(idx_fname) as index_file:
                for l in index_file:
                    yield l.strip().split(' ')

    @property
    def _context_fnames(self):
        if not hasattr(self, '_cfn'):
            self._read_graphs_index()
        return self._cfn

    @property
    def _fname_contexts(self):
        if not hasattr(self, '_fnc'):
            self._read_graphs_index()
        return self._fnc

    def _read_graphs_index(self):
        ctx_index = dict()
        fname_index = dict()
        for fname, ctx in self._graphs_index():
            ctx_index[ctx] = pth_join(self.powdir, 'graphs', fname)
            fname_index[fname] = ctx
        self._cfn = ctx_index
        self._fnc = fname_index

    def translate(self, translator, output_key=None, output_identifier=None,
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
            Output key. Used for generating the output's identifier. Exclusive with output_identifier
        output_identifier : str
            Output identifier. Exclusive with output_key
        data_sources : list of str
            Input data sources
        named_data_sources : dict
            Named input data sources
        """
        import transaction
        if named_data_sources is None:
            named_data_sources = dict()
        translator_obj = self._lookup_translator(translator)
        if translator_obj is None:
            raise GenericUserError('No translator for ' + translator)

        positional_sources = [self._lookup_source(src) for src in data_sources]
        if None in positional_sources:
            raise GenericUserError('No source for "' + data_sources[positional_sources.index(None)] + '"')
        named_sources = {k: self._lookup_source(src) for k, src in named_data_sources}
        with self._tempdir(prefix='pow-translate.') as d:
            orig_wd = os.getcwd()
            os.chdir(d)
            with transaction.manager:
                try:
                    res = translator_obj(*positional_sources,
                                         output_identifier=output_identifier,
                                         output_key=output_key,
                                         **named_sources)
                finally:
                    os.chdir(orig_wd)
                res.commit()
                res.context.save_context()

    @contextmanager
    def _tempdir(self, *args, **kwargs):
        td = pth_join(self.powdir, 'temp')
        if not exists(td):
            makedirs(td)
        kwargs['dir'] = td
        with TemporaryDirectory(*args, **kwargs) as d:
            yield d

    @property
    def _dsd(self):
        self._load_data_source_directories()
        return self._data_source_directories

    def _load_data_source_directories(self):
        if not self._data_source_directories:
            # The DSD holds mappings to data sources we've loaded before. In general, this allows the individual loaders
            # to not worry about checking if they have loaded something before.

            # XXX persist the dict
            lclasses = [POWDirDataSourceDirLoader()]
            dsd = _DSD(dict(), pth_join(self.powdir, 'data_source_data'), lclasses)
            try:
                dindex = open(pth_join(self.powdir, 'data_source_directories'))
                for ds_id, dname in (x.strip().split(' ', 1) for x in dindex):
                    dsd.put(ds_id, dname)
            except OSError:
                pass
            self._data_source_directories = dsd

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
        for x in self._data_ctx.stored(DataSource)(ident=self._den3(sname)).load():
            provide(x, self._cap_provs)
            return x

    @property
    def _cap_provs(self):
        return [DataSourceDirectoryProvider(self._dsd)]

    @property
    def _data_ctx(self):
        conf = self._conf()
        try:
            return Context(ident=conf[DATA_CONTEXT_KEY], conf=conf)
        except KeyError:
            raise ConfigMissingException(DATA_CONTEXT_KEY)

    def _make_ctx(self, ctxid):
        return Context(ident=ctxid, conf=self._conf())

    def reconstitute(self, data_source):
        '''
        Recreate a data source by executing the chain of translators that went into making it.

        Parameters
        ----------
        data_source : str
            Identifier for the data source to reconstitute
        '''

    def serialize(self, context=None, destination=None, format='nquads', include_imports=False, whole_graph=False):
        '''
        Serialize the current data context or the one provided

        Parameters
        ----------
        context : str
            The context to save
        destination : file or str
            A file-like object to write the file to or a file name. If not provided, messages the result.
        format : str
            Serialization format (ex, 'n3', 'nquads')
        include_imports : bool
            If true, then include contexts imported by the provided context in the result.
            The default is not to include imported contexts.
        whole_graph: bool
            Serialize all contexts from all graphs (this probably isn't what you want)
        '''

        retstr = False
        if destination is None:
            from six import BytesIO
            retstr = True
            destination = BytesIO()

        if context is None:
            ctx = self._data_ctx
        else:
            ctx = Context(ident=self._den3(context), conf=self._conf())

        if whole_graph:
            self._conf()['rdf.graph'].serialize(destination, format=format)
        else:
            if include_imports:
                ctx.stored.rdf_graph().serialize(destination, format=format)
            else:
                ctx.own_stored.rdf_graph().serialize(destination, format=format)

        if retstr:
            self.message(destination.getvalue().decode(encoding='utf-8'))

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
        for m in self.contexts.list():
            yield m

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

    def _changed_contexts_set(self):
        from rdflib.term import URIRef
        changed = set()
        gf_index = {URIRef(y): x for x, y in self._graphs_index()}
        for ctx, mtime in self._context_changed_times.items():
            g_fname = gf_index.get(ctx)
            g_fname = None if g_fname is None else pth_join(self.powdir, 'graphs', g_fname)
            if not g_fname or stat(g_fname).st_mtime != mtime:
                changed.add(ctx)
        changed |= set(gf_index.keys()) - set(self._context_changed_times.keys())
        return changed

    def _serialize_graphs(self, ignore_change_cache=False):
        import transaction
        from rdflib import plugin
        from rdflib.serializer import Serializer
        g = self._conf()['rdf.graph']
        repo = self.repository_provider

        repo.base = self.powdir
        graphs_base = pth_join(self.powdir, 'graphs')

        changed = self._changed_contexts_set()

        if changed and repo.is_dirty:
            repo.reset()

        if not exists(graphs_base):
            mkdir(graphs_base)

        files = []
        ctx_data = []

        with transaction.manager:
            for context in g.contexts():
                ident = context.identifier

                if not ignore_change_cache:
                    ctx_changed = ident in changed
                else:
                    ctx_changed = True

                sfname = self._context_fnames.get(str(ident))
                if not sfname:
                    fname = self._gen_ctx_fname(ident, graphs_base)
                else:
                    fname = sfname

                # If there's a context in the graph, but we don't even have a file, then it is changed.
                # This can happen if we get out of sync with what's on disk.
                if not ctx_changed and not exists(fname):
                    ctx_changed = True

                if ctx_changed:
                    # N.B. We *overwrite* changes to the serialized graphs -- the source of truth is what's in the
                    # RDFLib graph unless we regenerate the database
                    serializer = plugin.get('nt', Serializer)(sorted(context))
                    with open(fname, 'wb') as gfile:
                        serializer.serialize(gfile)
                self._context_changed_times[ident] = stat(fname).st_mtime
                ctx_data.append((relpath(fname, graphs_base), ident))
                files.append(fname)

        index_fname = pth_join(graphs_base, 'index')
        with open(index_fname, 'w') as index_file:
            for l in sorted(ctx_data):
                print(*l, file=index_file, end='\n')

        files.append(index_fname)
        repo.add([relpath(f, self.powdir) for f in files] + [relpath(self.config_file, self.powdir),
                                                             'graphs'])

    def _gen_ctx_fname(self, ident, graphs_base):
        hs = hashlib.sha256(ident.encode()).hexdigest()
        fname = pth_join(graphs_base, hs + '.nt')
        i = 1
        while exists(fname):
            fname = pth_join(graphs_base, hs + '-' + str(i) + '.nt')
            i += 1
        return fname

    def diff(self):
        """
        Show differences between what's in the working context set and what's in the serializations
        """
        import sys
        from difflib import unified_diff
        from os.path import join, basename
        import traceback
        from git import Repo

        r = self.repository_provider
        try:
            self._serialize_graphs(ignore_change_cache=False)
        except Exception:
            r.reset()
            L.exception("Could not serialize graphs")
            raise GenericUserError("Could not serialize graphs")

        head_commit = r.repo().head.commit
        di = head_commit.diff(None)

        for d in di:
            try:
                a_blob = d.a_blob
                if a_blob:
                    adata = a_blob.data_stream.read().split(b'\n')
                else:
                    adata = []
            except Exception as e:
                print('No "a" data: {}'.format(e), file=sys.stderr)
                adata = []

            try:
                b_blob = d.b_blob
                if b_blob:
                    bdata = b_blob.data_stream.read().split(b'\n')
                else:
                    with open(join(r.repo().working_dir, d.b_path), 'rb') as f:
                        bdata = f.read().split(b'\n')
            except Exception as e:
                print('No "b" data: {}'.format(e), file=sys.stderr)
                bdata = []
            afname = basename(d.a_path)
            bfname = basename(d.b_path)

            graphdir = join(self.powdir, 'graphs')
            fromfile = self._fname_contexts.get(afname, afname)
            tofile = self._fname_contexts.get(bfname, bfname)

            try:
                sys.stdout.writelines(
                        self._colorize_diff(unified_diff([x.decode('utf-8') + '\n' for x in adata],
                                     [x.decode('utf-8') + '\n' for x in bdata],
                                     fromfile='a ' + fromfile,
                                     tofile='b ' + tofile,
                                     lineterm='\n')))
            except Exception:
                if adata and not bdata:
                    sys.stdout.writelines('Deleted ' + fromfile + '\n')
                elif bdata and not adata:
                    sys.stdout.writelines('Created ' + fromfile + '\n')
                else:
                    asize = a_blob.size
                    asha = a_blob.hexsha
                    bsize = b_blob.size
                    bsha = b_blob.hexsha
                    sys.stdout.writelines(self._colorize_diff('''
                    --- a {fromfile}
                    --- Size: {asize}
                    --- Shasum: {asha}
                    +++ b {tofile}
                    +++ Size: {bsize}
                    +++ Shasum: {bsha}
                    '''.strip().format(locals())))

    def _colorize_diff(self, lines):
        from termcolor import colored
        for l in lines:
            if l.startswith('+'):
                yield colored(l, 'green')
            elif l.startswith('-'):
                yield colored(l, 'red')
            else:
                yield l

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

    def __init__(self, backer, user_module=None):
        self._user_mod = user_module
        self._backer = backer  #: Backing context
        self._imported_ctx_ids = set([self._backer.identifier])
        self._unvalidated_statements = []

    def add_import(self, ctx):
        self._imported_ctx_ids.add(ctx.identifier)
        # Remove unvalidated statements which had this new context as the one they are missing
        self._unvalidated_statements = [p for p in self._unvalidated_statements if p[2][0] != ctx.identifier]
        return self._backer.add_import(ctx)

    def add_statement(self, stmt):
        stmt_tuple = (stmt.subject, stmt.property, stmt.object)
        for p in (UnimportedContextRecord(x.context.identifier, i, stmt) for i, x in enumerate(stmt_tuple)
                  if x.context is not None and x.context.identifier not in self._imported_ctx_ids):
            from inspect import getouterframes, currentframe
            self._unvalidated_statements.append(SaveValidationFailureRecord(self._user_mod,
                                                                            getouterframes(currentframe()),
                                                                            p))
        return self._backer.add_statement(stmt)

    def __getattr__(self, name):
        return getattr(self._backer, name)

    def save_context(self, *args, **kwargs):
        return self._backer.save_context(*args, **kwargs)

    def save_imports(self, *args, **kwargs):
        return self._backer.save_imports(*args, **kwargs)


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


class SaveValidationFailureRecord(namedtuple('SaveValidationFailureRecord', ['user_module',
                                                                             'stack',
                                                                             'validation_record'])):

    def filtered_stack(self):
        umfile = getattr(self.user_module, '__file__', None)
        if umfile and umfile.endswith('pyc'):
            umfile = umfile[:-3] + 'py'
        ourfile = __file__

        if ourfile.endswith('pyc'):
            ourfile = ourfile[:-3] + 'py'

        def find_last_user_frame(frames):
            start = False
            lastum = 0
            res = []
            for i, f in enumerate(frames):
                if umfile and f[1].startswith(umfile):
                    lastum = i
                if start:
                    res.append(f)
                if not start and f[1].startswith(ourfile):
                    start = True
            return res[:lastum]

        return find_last_user_frame(self.stack)

    def __str__(self):
        from traceback import format_list
        stack = format_list([x[1:4] + (''.join(x[4]).strip(),) for x in self.filtered_stack()])
        fmt = '{}\n Traceback (most recent call last, PyOpenWorm frames omitted):\n {}'
        res = fmt.format(self.validation_record, '\n '.join(''.join(s for s in stack if s).split('\n')))
        return res.strip()


class _DSD(object):
    def __init__(self, ds_dict, base_directory, loaders):
        self._dsdict = ds_dict
        self._base_directory = base_directory
        self._loaders = self._init_loaders(loaders)

    def __getitem__(self, data_source):
        dsid = str(data_source.identifier)
        try:
            return self._dsdict[dsid]
        except KeyError:
            res = self._load_data_source(data_source)
            if res:
                self._dsdict[dsid] = res
                return res
            raise

    def put(self, data_source_ident, directory):
        self._dsdict[str(data_source_ident)] = directory

    def _init_loaders(self, loaders):
        res = []
        for loader in loaders:
            nd = pth_join(self._base_directory, loader.directory_key)
            if not exists(nd):
                makedirs(nd)
            loader.base_directory = nd
            res.append(loader)
        return res

    def _load_data_source(self, data_source):
        for loader in self._loaders:
            if loader.can_load(data_source):
                return loader(data_source)


class DataSourceDirectoryProvider(FilePathProvider):
    def __init__(self, dsd):
        self._dsd = dsd

    def __call__(self, ob):
        try:
            path = self._dsd[ob]
        except KeyError:
            return None

        return _DSDP(path)


class _DSDP(FilePathProvider):
    def __init__(self, path):
        self._path = path

    def file_path(self):
        return self._path


class POWDirDataSourceDirLoader(DataSourceDirLoader):
    def __init__(self, basedir=None):
        super(POWDirDataSourceDirLoader, self).__init__()
        self._index = dict()
        self.base_directory = basedir

    @property
    def base_directory(self):
        return self._base_directory

    @base_directory.setter
    def base_directory(self, val):
        if val:
            self._base_directory = val
            self._idx_fname = pth_join(val, 'index')

    def _load_index(self):
        with scandir(self._base_directory) as dirents:
            dentdict = {de.name: de for de in dirents}
            with open(self._idx_fname) as f:
                for l in f:
                    dsid, dname = l.split(' ')
                    dname = dname.strip()
                    if self._index_dir_entry_is_bad(dname, dentdict.get(dname)):
                        continue

                    self._index[dsid] = dname

    def _index_dir_entry_is_bad(self, dname, de):
        if not de:
            msg = "There is no directory entry for {} in {}"
            L.warn(msg.format(dname, self._base_directory), exc_info=True)
            return True

        if not de.is_dir():
            msg = "The directory entry for {} in {} is not a directory"
            L.warn(msg.format(dname, self._base_directory))
            return True

        return False

    def _ensure_index_loaded(self):
        if not self._index:
            self._load_index()

    def can_load(self, data_source):
        try:
            self._ensure_index_loaded()
        except (OSError, IOError) as e:
            # If the index file just happens not to be here since the repo doesn't have any data source directories,
            # then we just can't load the data source's data, but for any other kind of error, something more exotic
            # could be the cause, so let the caller handle it
            #
            if e.errno == 2: # FileNotFound
                return False
            raise
        return str(data_source.identifier) in self._index

    def load(self, ident):
        try:
            self._ensure_index_loaded()
        except Exception as e:
            raise LoadFailed(ident, self, "Failed to load the index: " + str(e))

        try:
            return self._index[ident]
        except KeyError:
            raise LoadFailed(ident, self, 'The given identifier is not in the index')


class POWSaveNamespace(object):
    def __init__(self, context):
        self.context = context
        self._created_ctxs = set()
        self._external_contexts = set()

    def new_context(self, ctx_id):
        # Get the type of our context contextualized *with* our context
        ctx_type = self.context(type(self.context))

        # Make the "backing" context for the result we return
        new_ctx = self.context(Context)(ident=ctx_id, conf=self.context.conf)

        # Make the "wrapper" context and pass through the user's module for validation
        res = ctx_type(new_ctx, user_module=self.context._user_mod)

        # Finally, add the context
        self._created_ctxs.add(res)
        return res

    def include_context(self, ctx):
        '''
        Include the given exernally-created context for saving.

        If you the context is being made within the save function, then you can use new_context instead.
        '''
        self._external_contexts.add(ctx)

    def created_contexts(self):
        for ctx in self._created_ctxs:
            yield ctx
        yield self.context

    def validate(self):
        unvalidated = []
        for c in self._created_ctxs:
            unvalidated += c._unvalidated_statements
        unvalidated += self.context._unvalidated_statements
        if unvalidated:
            raise StatementValidationError(unvalidated)

    def save(self, *args, **kwargs):
        self.validate()
        for c in self._created_ctxs:
            c.save_context(*args, **kwargs)

        for c in self._external_contexts:
            c.save_context(*args, **kwargs)
        return self.context.save_context(*args, **kwargs)


class UnimportedContextRecord(namedtuple('UnimportedContextRecord', ['context', 'node_index', 'statement'])):
    def __str__(self):
        from yarom.rdfUtils import triple_to_n3
        trip = self.statement.to_triple()
        fmt = 'Missing import of context {} for {} of statement "{}"'
        return fmt.format(self.context.n3(),
                          trip[self.node_index].n3(),
                          triple_to_n3(trip))


class StatementValidationError(GenericUserError):
    def __init__(self, statements):
        msgfmt = '{} invalid statements were found:\n{}'
        msg = msgfmt.format(len(statements), '\n'.join(str(x) for x in statements))
        super(StatementValidationError, self).__init__(msg)
        self.statements = statements


class ConfigMissingException(GenericUserError):
    def __init__(self, key):
        self.key = key
