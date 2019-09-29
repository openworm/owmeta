import re
from yarom.utils import FCN
from yarom.rdfUtils import transitive_lookup, BatchAddGraph
from os.path import join as p, exists, relpath, expanduser
from os import makedirs, rename
import hashlib
import shutil
import errno
from rdflib.term import URIRef
from struct import pack
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


class DirectoryLoader(object):
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
        raise NotImplementedError()


class Remote(object):
    '''
    A place where bundles come from and go to
    '''


class Descriptor(object):
    '''
    Descriptor for a bundle
    '''
    def __init__(self, ident):
        self.id = ident
        self.name = None
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
        res.description = obj.get('description', None)
        res.patterns = set(make_pattern(x) for x in obj.get('patterns', ()))
        res.includes = set(make_include_func(x) for x in obj.get('includes', ()))
        res.files = FilesDescriptor.make(obj.get('files', None))
        return res

    def __str__(self):
        return (FCN(type(self)) + '(ident={},'
                'name={},description={},'
                'patterns={},includes={},'
                'files={})').format(
                        repr(self.id),
                        repr(self.name),
                        repr(self.description),
                        repr(self.patterns),
                        repr(self.includes),
                        repr(self.files))


class Bundle(object):
    def __init__(self, ident, bundles_directory=None, conf=None):
        if not ident:
            raise Exception('ident must be non-None')
        self.ident = ident
        if bundles_directory is None:
            bundles_directory = expanduser(p('~', '.owmeta', 'bundles'))
        self.bundles_directory = bundles_directory
        if not conf:
            conf = {'rdf.source': 'sqlite'}
        self._given_conf = conf
        self.conf = None

    def _get_bundle(self):
        # - look up the bundle in the index
        # - generate a config based on the current config load the config
        # - make a database from the graphs, if necessary (similar to `owm regendb`). If
        #   delete the existing database if it doesn't match the store config
        bdir = bundle_directory(self.bundles_directory, self.ident)
        self._make_config(bdir)

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


def bundle_directory(bundles_directory, ident):
    return p(bundles_directory, urlquote(ident, safe=''))


class Installer(object):
    '''
    Installs a bundle locally
    '''

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
            Name of this installer for purposes of mutual exclusion
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
        '''
        # Create the staging directory in the base directory to reduce the chance of
        # moving across file systems
        try:
            staging_directory = bundle_directory(self.bundles_directory, descriptor.id)
            makedirs(staging_directory)
        except OSError:
            pass
        with lock_file(p(staging_directory, '.lock'), unique_key=self.installer_id):
            try:
                self._install(descriptor, staging_directory)
            except Exception:
                self._cleanup_failed_install(staging_directory)
                raise

    def _cleanup_failed_install(self, staging_directory):
        shutil.rmtree(p(staging_directory, 'graphs'))
        shutil.rmtree(p(staging_directory, 'files'))

    def _install(self, descriptor, staging_directory):
        contexts = _select_contexts(descriptor, self.graph)
        graphs_directory = p(staging_directory, 'graphs')
        files_directory = p(staging_directory, 'files')
        try:
            makedirs(graphs_directory)
            makedirs(files_directory)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        with open(p(files_directory, 'hashes'), 'wb') as hash_out:
            for fname in _select_files(descriptor, self.source_directory):
                hsh = self.file_hash()
                source_fname = p(self.source_directory, fname)
                with open(source_fname, 'rb') as fh:
                    hash_file(hsh, fh)
                hash_out.write(fname.encode('UTF-8') + b'\x00' + pack('B', hsh.digest_size) + hsh.digest() + b'\n')
                shutil.copy2(source_fname, p(files_directory, fname))

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
                hash_out.write(ctxidb + b'\x00' + pack('B', hsh.digest_size) + hsh.digest() + b'\n')
                hash_out.flush()
                gbname = hsh.hexdigest() + '.nt'
                ctx_file_name = p(graphs_directory, gbname)
                rename(temp_fname, ctx_file_name)
                index_out.write(ctxidb + b'\x00' + gbname.encode('UTF-8') + b'\n')
                index_out.flush()

                if self.imports_ctx and imports_ctxg:
                    imported_contexts |= transitive_lookup(self.imports_ctxg,
                                                           ctxid,
                                                           CONTEXT_IMPORTS,
                                                           seen=imported_contexts)
                # Get transitive imports and include in the new imports context

        with open(p(staging_directory, 'manifest'), 'wb') as mf:
            if self.data_ctx:
                mf.write(DATA_CONTEXT_KEY.encode('UTF-8') + b'\x00' +
                        self.data_ctx.encode('UTF-8') + b'\n')
            if self.imports_ctx:
                mf.write(IMPORTS_CONTEXT_KEY.encode('UTF-8') + b'\x00' +
                         b'http://openworm.org/data/generated_imports_ctx?bundle_id=' +
                         quote(descriptor.id).encode('UTF-8') + b'\n')
            mf.flush()


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
