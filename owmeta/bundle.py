import re
from yarom.utils import FCN
from yarom.rdfUtils import transitive_lookup, BatchAddGraph
from os.path import join as p, exists, relpath, expanduser
from os import makedirs, rename, scandir
import hashlib
import shutil
import errno
from rdflib.term import URIRef
from struct import pack
import yaml
from .context import DATA_CONTEXT_KEY, IMPORTS_CONTEXT_KEY
from .context_common import CONTEXT_IMPORTS
from .data import Data
from .file_match import match_files
from .file_lock import lock_file
from .graph_serialization import write_canonical_to_file, gen_ctx_fname

try:
    from urllib.parse import quote as urlquote
except ImportError:
    from urllib import quote as urlquote


class Remote(object):
    '''
    A place where bundles come from and go to
    '''
    def __init__(self, name, accessor_configs=()):
        '''
        Parameters
        ----------
        name : str
            The name of the remote
        '''

        self.name = name
        ''' Name of the remote '''

        self.accessor_configs = list(accessor_configs)
        ''' Configs for how you access the remote. Probably just URLs '''

        self._loaders = []

    def add_config(self, accessor_config):
        self.accessor_configs.append(accessor_config)

    def generate_loaders(self, loader_classes):
        '''
        Generate

        Parameters
        ----------
        loader_classes : list of Loader subclasses
            List of
        '''
        self._loaders = []
        for ac in self.accessor_configs:
            for lc in loader_classes:
                if lc.can_load_from(ac):
                    loader = lc(ac)
                    self._loaders.append(loader)
                    yield loader

    def write(self, out):
        '''
        Serialize the `Remote` and write to `out`

        Parameters
        ----------
        out : :term:`file object`
            Target for writing the remote
        '''
        yaml.dump(self, out)

    @classmethod
    def read(cls, inp):
        '''
        Read a serialized `Remote`

        Parameters
        ----------
        inp : :term:`file object`
            File-like object containing the serialized `Remote`
        '''
        res = yaml.full_load(inp)
        assert isinstance(res, cls)
        return res

    def __eq__(self, other):
        return (self.name == other.name and
                self.accessor_configs == other.accessor_configs)


class AccessorConfig(object):
    '''
    Configuration for accessing a remote. Loaders are added to a remote according to which
    accessors are avaialble
    '''

    def __eq__(self, other):
        raise NotImplementedError()


class URLConfig(AccessorConfig):
    '''
    Configuration for accessing a remote with just a URL.
    '''

    def __init__(self, url):
        self.url = url

    def __eq__(self, other):
        return self.url == other.url

    def __str__(self):
        return '{}(url={})'.format(FCN(type(self)), repr(self.url))

    __repr__ = __str__


class Descriptor(object):
    '''
    Descriptor for a bundle
    '''
    def __init__(self, ident):
        self.id = ident
        self.name = None
        self.version = 1
        self.description = None
        self.patterns = set()
        self.includes = set()
        self.files = None

    @classmethod
    def make(cls, obj):
        '''
        Makes a descriptor from the given object.
        '''
        res = cls(ident=obj['id'])
        res.name = obj.get('name', obj['id'])
        res.version = obj.get('version', 1)
        res.description = obj.get('description', None)
        res.patterns = set(make_pattern(x) for x in obj.get('patterns', ()))
        res.includes = set(make_include_func(x) for x in obj.get('includes', ()))
        res.files = FilesDescriptor.make(obj.get('files', None))
        return res

    def __str__(self):
        return (FCN(type(self)) + '(ident={},'
                'name={},version={},description={},'
                'patterns={},includes={},'
                'files={})').format(
                        repr(self.id),
                        repr(self.name),
                        repr(self.version),
                        repr(self.description),
                        repr(self.patterns),
                        repr(self.includes),
                        repr(self.files))


class Bundle(object):
    def __init__(self, ident, bundles_directory=None, version=None, conf=None):
        if not ident:
            raise Exception('ident must be non-None')
        self.ident = ident
        if bundles_directory is None:
            bundles_directory = expanduser(p('~', '.owmeta', 'bundles'))
        self.bundles_directory = bundles_directory
        if not conf:
            conf = {'rdf.source': 'sqlite'}
        self.version = version
        self._given_conf = conf
        self.conf = None

    def _get_bundle_directory(self):
        # - look up the bundle in the index
        # - generate a config based on the current config load the config
        # - make a database from the graphs, if necessary (similar to `owm regendb`). If
        #   delete the existing database if it doesn't match the store config
        version = self.version
        if version is None:
            bundle_root = bundle_directory(self.bundles_directory, self.ident)
            latest_version = 0
            try:
                ents = scandir(bundle_root)
            except (OSError, IOError) as e:
                if e.errno == 2: # FileNotFound
                    raise BundleNotFound(self.ident, 'Bundle directory does not exist')
                raise

            for ent in ents:
                if ent.is_dir():
                    try:
                        vn = int(ent.name)
                    except ValueError:
                        # We may put things other than versioned bundle directories in
                        # this directory later, in which case this is OK
                        pass
                    else:
                        if vn > latest_version:
                            latest_version = vn
            version = latest_version
        if not version:
            raise BundleNotFound(self.ident, 'No versioned bundle directories exist')
        res = bundle_directory(self.bundles_directory, self.ident, version)
        if not exists(res):
            if self.version is None:
                raise BundleNotFound(self.ident, 'Bundle directory does not exist', version)
            else:
                raise BundleNotFound(self.ident, 'Bundle directory does not exist for the specified version', version)
        return res

    def _get_bundle(self):
        self._make_config(self._get_bundle_directory())

    def _make_config(self, bundle_directory, progress=None, trip_prog=None):
        self.conf = Data().copy(self._given_conf)
        self.conf['rdf.store_conf'] = p(bundle_directory, 'owm.db')
        self.conf[IMPORTS_CONTEXT_KEY] = (
                'http://openworm.org/data/generated_imports_ctx?bundle_id=' + urlquote(self.ident))
        with open(p(bundle_directory, 'manifest')) as mf:
            data_ctx = None
            imports_ctx = None
            for ln in mf:
                if ln.startswith(DATA_CONTEXT_KEY):
                    self.conf[DATA_CONTEXT_KEY] = ln[len(DATA_CONTEXT_KEY) + 1:]
                if ln.startswith(IMPORTS_CONTEXT_KEY):
                    self.conf[IMPORTS_CONTEXT_KEY] = ln[len(IMPORTS_CONTEXT_KEY) + 1:]
        # Create the database file and initialize some needed data structures
        self.conf.init()
        if not exists(self.conf['rdf.store_conf']):
            raise Exception('Cannot find the database file at ' + self.conf['rdf.store_conf'])
        self._load_all_graphs(bundle_directory, progress=progress, trip_prog=trip_prog)

    def _load_all_graphs(self, bundle_directory, progress=None, trip_prog=None):
        # This is very similar to the owmeta.command.OWM._load_all_graphs, but is
        # different enough that it's easier to just keep them separate
        import transaction
        from rdflib import plugin
        from rdflib.parser import Parser, create_input_source
        graphs_directory = p(bundle_directory, 'graphs')
        idx_fname = p(graphs_directory, 'index')
        if not exists(idx_fname):
            raise Exception('Cannot find an index at {}'.format(repr(idx_fname)))
        triples_read = 0
        dest = self.rdf
        with open(idx_fname, 'rb') as index_file:
            if progress is not None:
                cnt = 0
                for l in index_file:
                    cnt += 1
                index_file.seek(0)

                progress.total = cnt

            parser = plugin.get('nt', Parser)()
            with transaction.manager:
                for l in index_file:
                    l = l.strip()
                    if not l:
                        continue
                    ctx, fname = l.split(b'\x00')
                    graph_fname = p(graphs_directory, fname.decode('UTF-8'))
                    with open(graph_fname, 'rb') as f, \
                            BatchAddGraph(dest.get_context(ctx.decode('UTF-8')), batchsize=4000) as g:
                        parser.parse(create_input_source(f), g)

                    if progress is not None and trip_prog is not None:
                        progress.update(1)
                        triples_read += g.count
                        trip_prog.update(g.count)
                if progress is not None:
                    progress.write('Finalizing writes to database...')
        if progress is not None:
            progress.write('Loaded {:,} triples'.format(triples_read))

    @property
    def rdf(self):
        return self.conf['rdf.graph']

    def __enter__(self):
        self._get_bundle()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.conf.destroy()

    def __call__(self, target):
        if target and hasattr(target, 'contextualize'):
            return target.contextualie(self)
        return None


def bundle_directory(bundles_directory, ident, version=None):
    '''
    Get the directory for the given bundle identifier and version

    Parameters
    ----------
    ident : str
        Bundle identifier
    version : int
        Version number. If not provided, returns the directory containing all of the
        versions
    '''
    base = p(bundles_directory, urlquote(ident, safe=''))
    if version is not None:
        return p(base, str(version))
    else:
        return base


class Loader(object):
    '''
    Downloads bundles into the local index and caches them

    Attributes
    ----------
    base_directory : str
        The path where the bundle archive should be unpacked
    '''

    def __init__(self):
        # The base directory
        self.base_directory = None

    @classmethod
    def can_load_from(cls, accessor_config):
        ''' Returns True if the given accessor_config is a valid config for this loader '''
        return False

    def can_load(self, bundle_name):
        ''' Returns True if the bundle named `bundle_name` is supported '''
        return False

    def load(self, bundle_name):
        ''' Loads the bundle into the local index '''
        raise NotImplementedError()

    def __call__(self, bundle_name):
        return self.load(bundle_name)


class HTTPBundleLoader(Loader):
    # TODO: Test this class...
    '''
    Loads bundles from HTTP(S) resources listed in an index file
    '''

    def __init__(self, index_url, cachedir=None, **kwargs):
        '''
        Parameters
        ----------
        index_url : str or URLConfig
            URL for the index file pointing to the bundle archives
        cachedir : str
            Directory where the index and any downloaded bundle archive should be cached.
            If provided, the index and bundle archive is cached in the given directory. If
            not provided, the index will be cached in memory and the bundle will not be
            cached.
        '''
        super(HTTPBundleLoader, self).__init__(**kwargs)

        if isinstance(index_url, str):
            self.index_url = index_url
        elif isinstance(index_url, URLConfig):
            self.index_url = index_url.url
        else:
            raise TypeError('Expecting a string or URLConfig. Received %s' %
                    type(index_url))

        self.cachedir = cachedir
        self._index = None

    def _setup_index(self):
        import requests
        if self._index is None:
            response = requests.get(self.index_url)
            self._index = response.json()

    @classmethod
    def can_load_from(cls, ac):
        return (isinstance(ac, URLConfig) and
                (ac.url.startswith('https://') or
                    ac.url.startswith('http://')))

    def can_load(self, bundle_name):
        self._setup_index()
        return bundle_name in self._index

    def load(self, bundle_name):
        '''
        Loads a bundle by downloading an index file
        '''
        import requests
        self._setup_index()
        bundle_url = self._index.get(bundle_name)
        if not bundle_url:
            raise LoadFailed(bundle_name, self, 'Bundle is not in the index')
        response = requests.get(bundle_url, stream=True)
        if self.cachedir is not None:
            bfn = urlquote(bundle_name)
            with open(p(self.cachedir, bfn), 'w') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)
            with open(p(self.cachedir, bfn), 'r') as f:
                self._unpack(f)
        else:
            self._unpack(response.raw)

    def _unpack(self, f):
        import tarfile
        with tarfile.open(mode='r:xz', fileobj=f) as ba:
            ba.extractall(self.base_directory)


class DirectoryLoader(Loader):
    '''
    Loads a bundle into a directory.

    Created from a remote to actually get the bundle
    '''
    def __init__(self, base_directory=None):
        self.base_directory = base_directory

    def load(self, bundle_name):
        '''
        Loads a bundle into the given base directory
        '''
        super(DirectoryLoader, self).load(bundle_name)


class Installer(object):
    '''
    Installs a bundle locally
    '''

    # TODO: Make source_directory optional -- not every bundle needs files
    def __init__(self, source_directory, bundles_directory, graph,
                 imports_ctx=None, data_ctx=None, installer_id=None):
        '''
        Parameters
        ----------
        source_directory : str
            Directory where files come from
        bundles_directory : str
            Directory where the bundles files go
        installer_id : str
            Name of this installer for purposes of mutual exclusion. optional
        '''
        self.context_hash = hashlib.sha224
        self.file_hash = hashlib.sha224
        self.source_directory = source_directory
        self.bundles_directory = bundles_directory
        self.graph = graph
        self.installer_id = installer_id
        self.imports_ctx = imports_ctx
        self.data_ctx = data_ctx

    def install(self, descriptor):
        '''
        Given a descriptor, install a bundle

        Parameters
        ----------
        descriptor : Descriptor
            The descriptor for the bundle

        Returns
        -------
            The directory where the bundle is installed
        '''
        # Create the staging directory in the base directory to reduce the chance of
        # moving across file systems
        try:
            staging_directory = bundle_directory(self.bundles_directory, descriptor.id,
                    descriptor.version)
            makedirs(staging_directory)
        except OSError:
            pass

        with lock_file(p(staging_directory, '.lock'), unique_key=self.installer_id):
            try:
                self._install(descriptor, staging_directory)
                return staging_directory
            except Exception:
                self._cleanup_failed_install(staging_directory)
                raise

    def _cleanup_failed_install(self, staging_directory):
        shutil.rmtree(p(staging_directory, 'graphs'))
        shutil.rmtree(p(staging_directory, 'files'))

    def _install(self, descriptor, staging_directory):
        graphs_directory, files_directory = self._set_up_directories(staging_directory)
        self._write_file_hashes(descriptor, files_directory)
        self._write_context_data(descriptor, graphs_directory)
        self._write_manifest(descriptor, staging_directory)

    def _set_up_directories(self, staging_directory):
        graphs_directory = p(staging_directory, 'graphs')
        files_directory = p(staging_directory, 'files')

        try:
            makedirs(graphs_directory)
            makedirs(files_directory)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        return graphs_directory, files_directory

    def _write_file_hashes(self, descriptor, files_directory):
        with open(p(files_directory, 'hashes'), 'wb') as hash_out:
            for fname in _select_files(descriptor, self.source_directory):
                hsh = self.file_hash()
                source_fname = p(self.source_directory, fname)
                with open(source_fname, 'rb') as fh:
                    hash_file(hsh, fh)
                hash_out.write(fname.encode('UTF-8') + b'\x00' + pack('B', hsh.digest_size) + hsh.digest() + b'\n')
                shutil.copy2(source_fname, p(files_directory, fname))

    def _write_manifest(self, descriptor, staging_directory):
        with open(p(staging_directory, 'manifest'), 'wb') as mf:
            if self.data_ctx:
                mf.write(DATA_CONTEXT_KEY.encode('UTF-8') + b'\x00' +
                        self.data_ctx.encode('UTF-8') + b'\n')
            if self.imports_ctx:
                mf.write(IMPORTS_CONTEXT_KEY.encode('UTF-8') + b'\x00' +
                         b'http://openworm.org/data/generated_imports_ctx?bundle_id=' +
                         quote(descriptor.id).encode('UTF-8') + b'\n')
            mf.write(b'version\x00' + pack('Q', descriptor.version) + b'\n')
            mf.flush()

    def _write_context_data(self, descriptor, graphs_directory):
        contexts = _select_contexts(descriptor, self.graph)

        # XXX: Find out what I was planning to do with these imported contexts...adding
        # dependencies or something?
        if self.imports_ctx:
            imports_ctxg = self.graph.get_context(self.imports_ctx)

        with open(p(graphs_directory, 'hashes'), 'wb') as hash_out,\
                open(p(graphs_directory, 'index'), 'wb') as index_out:
            imported_contexts = set()
            for ctxid, ctxgraph in contexts:
                hsh = self.context_hash()
                temp_fname = p(graphs_directory, 'graph.tmp')
                write_canonical_to_file(ctxgraph, temp_fname)
                with open(temp_fname, 'rb') as ctx_fh:
                    hash_file(hsh, ctx_fh)
                ctxidb = ctxid.encode('UTF-8')
                # Write hash
                hash_out.write(ctxidb + b'\x00' + pack('B', hsh.digest_size) + hsh.digest() + b'\n')
                gbname = hsh.hexdigest() + '.nt'
                # Write index
                index_out.write(ctxidb + b'\x00' + gbname.encode('UTF-8') + b'\n')

                ctx_file_name = p(graphs_directory, gbname)
                rename(temp_fname, ctx_file_name)

                if self.imports_ctx and imports_ctxg:
                    imported_contexts |= transitive_lookup(imports_ctxg,
                                                           ctxid,
                                                           CONTEXT_IMPORTS,
                                                           seen=imported_contexts)
            hash_out.flush()
            index_out.flush()


def hash_file(hsh, fh, blocksize=None):
    '''
    Hash a file in chunks to avoid eating up too much memory at a time
    '''
    if not blocksize:
        blocksize = hsh.block_size << 15
    while True:
        block = fh.read(blocksize)
        if not block:
            break
        hsh.update(block)


class IndexManager(object):
    def __init__(self):
        self.index = None

    def add_entry(self, bundle):
        bundle_descriptor.files


class IndexEntry(object):
    '''
    An index entry.

    Points to the attached files and contexts
    '''

    def __init__(self):
        self.file_refs = set()
        ''' References to files in this bundle '''

        self.context_files = set()
        ''' A list of files in this bundle '''


class FilesDescriptor(object):
    '''
    Descriptor for files
    '''
    def __init__(self):
        self.patterns = set()
        self.includes = set()

    @classmethod
    def make(cls, obj):
        if not obj:
            return
        res = cls()
        res.patterns = set(obj.get('patterns', ()))
        res.includes = set(obj.get('includes', ()))
        return res


def make_pattern(s):
    if s.startswith('rgx:'):
        return RegexURIPattern(s[4:])
    else:
        return GlobURIPattern(s)


def make_include_func(s):
    return URIIncludeFunc(s)


class URIIncludeFunc(object):

    def __init__(self, include):
        self.include = URIRef(include.strip())

    def __hash__(self):
        return hash(self.include)

    def __call__(self, uri):
        return uri == self.include

    def __str__(self):
        return '{}({})'.format(FCN(type(self)), repr(self.include))

    __repr__ = __str__


class URIPattern(object):
    def __init__(self, pattern):
        self._pattern = pattern

    def __hash__(self):
        return hash(self._pattern)

    def __call__(self, uri):
        return False

    def __str__(self):
        return '{}({})'.format(FCN(type(self)), self._pattern)


class RegexURIPattern(URIPattern):
    def __init__(self, pattern):
        super(RegexURIPattern, self).__init__(re.compile(pattern))

    def __call__(self, uri):
        # Cast the pattern match result to a boolean
        return not not self._pattern.match(str(uri))


class GlobURIPattern(RegexURIPattern):
    def __init__(self, pattern):
        replacements = [
            ['*', '.*'],
            ['?', '.?'],
            ['[!', '[^']
        ]

        for a, b in replacements:
            pattern = pattern.replace(a, b)
        super(GlobURIPattern, self).__init__(re.compile(pattern))


def _select_files(descriptor, directory):
    fdescr = descriptor.files
    if not fdescr:
        return
    for f in fdescr.includes:
        if not exists(p(directory, f)):
            raise Exception('Included file in bundle does not exist', f)
        yield f

    for f in fdescr.patterns:
        for match in match_files(directory, p(directory, f)):
            yield relpath(match, directory)


def _select_contexts(descriptor, graph):
    for context in graph.contexts():
        ctx = context.identifier
        for inc in descriptor.includes:
            if inc(ctx):
                yield ctx, context
                break

        for pat in descriptor.patterns:
            if pat(ctx):
                yield ctx, context
                break


class BundleNotFound(Exception):
    def __init__(self, bundle_ident, msg=None, version=None):
        msg = 'Missing bundle "{}"{}{}'.format(bundle_ident,
                '' if version is None else ' at version ' + str(version),
                ': ' + str(msg) if msg is not None else '')
        super(BundleNotFound, self).__init__(msg)


class LoadFailed(Exception):
    def __init__(self, bundle, loader, *args):
        msg = args[0]
        mmsg = 'Failed to load {} bundle with loader {}{}'.format(
                bundle, loader, ': ' + msg if msg else '')
        super(LoadFailed, self).__init__(mmsg, *args[1:])
