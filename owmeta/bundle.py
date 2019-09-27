import re
from yarom.utils import FCN
from os.path import join as p, exists, relpath
from os import makedirs, rename
import hashlib
import shutil
import errno
from rdflib.term import URIRef
from struct import pack
from .file_match import match_files
from .file_lock import lock_file
from .graph_serialization import write_canonical_to_file, gen_ctx_fname

try:
    from urllib.parse import quote as urlquote
except ImportError:
    from urllib import quote as urlquote


class BundleLoader(object):
    '''
    Loads a bundle.
    '''
    def __init__(self, base_directory=None):
        self.base_directory = base_directory

    def load(self, bundle_name):
        '''
        Loads a bundle into the given base directory
        '''
        raise NotImplementedError()


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


class Bundle(object):
    def __init__(self, ident):
        pass

    @property
    def rdf(self):
        pass


class Installer(object):
    '''
    Installs a bundle locally
    '''

    def __init__(self, source_directory, index_directory, bundles_directory, graph,
                 installer_id=None):
        '''
        Parameters
        ----------
        source_directory : str
            Directory where files come from
        index_directory : str
            Directory where the index file goes
        bundles_directory : str
            Directory where the bundles files go
        installer_id : str
            Name of this installer for purposes of mutual exclusion
        '''
        self.context_hash = hashlib.sha224
        self.file_hash = hashlib.sha224
        self.source_directory = source_directory
        self.index_directory = index_directory
        self.bundles_directory = bundles_directory
        self.graph = graph
        self.installer_id = installer_id

    def install(self, descriptor):
        '''
        Given a descriptor, install a bundle
        '''
        # Create the staging directory in the base directory to reduce the chance of
        # moving across file systems
        try:
            staging_directory = p(self.bundles_directory, urlquote(descriptor.id, safe=''))
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

        with open(p(graphs_directory, 'hashes'), 'wb') as hash_out,\
                open(p(graphs_directory, 'index'), 'wb') as index_out:
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
                hash_out.write(ctxidb + b'\x00' + gbname.encode('UTF-8') + b'\n')
                index_out.write(ctxidb)


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
