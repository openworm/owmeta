'''
Bundle commands
'''
from __future__ import print_function
import logging
import shutil
import hashlib
from os.path import join as p, abspath, relpath, isdir
from os import mkdir, listdir, unlink
import yaml
from ..context import DEFAULT_CONTEXT_KEY, IMPORTS_CONTEXT_KEY
from ..command_util import GenericUserError, GeneratorWithData, SubCommand
from ..bundle import (Descriptor,
                      Installer,
                      URLConfig,
                      Remote,
                      Fetcher,
                      Cache,
                      Unarchiver,
                      retrieve_remotes,
                      fmt_bundle_directory,
                      NoBundleLoader as _NoBundleLoader)

import hashlib


L = logging.getLogger(__name__)


class OWMBundleRemote(object):
    ''' Commands for dealing with bundle remotes '''

    def __init__(self, parent):
        self._parent = parent
        self._owm = self._parent._parent

    def add(self, name, url):
        '''
        Add a remote

        Parameters
        ----------
        name : str
            Name of the remote
        url : str
            URL for the remote
        '''
        url = URLConfig(url)
        r = Remote(name, accessor_configs=(url,))
        remotes_dir = p(self._owm.owmdir, 'remotes')
        if not isdir(remotes_dir):
            try:
                mkdir(remotes_dir)
            except Exception:
                L.warning('Could not crerate directory for storage of remote configurations', exc_info=True)
                raise GenericUserError('Could not create directory for storage of remote configurations')

        fname = self._remote_fname(r.name)
        try:
            with open(fname, 'w') as out:
                r.write(out)
        except Exception:
            unlink(fname)
            raise

    def _remote_fname(self, name):
        return p(self._owm.owmdir, 'remotes', hashlib.sha224(name.encode('UTF-8')).hexdigest() + '.remote')

    def list(self):
        ''' List remotes '''

        def helper():
            remotes_dir = p(self._owm.owmdir, 'remotes')
            for r in listdir(remotes_dir):
                if r.endswith('.remote'):
                    with open(p(remotes_dir, r)) as inp:
                        try:
                            yield Remote.read(inp)
                        except Exception:
                            L.warning('Unable to read remote %s', r, exc_info=True)

        return GeneratorWithData(helper(),
                text_format=lambda r: r.name,
                columns=(lambda r: r.name,),
                header=("Name",))


class OWMBundleCache(object):
    '''
    Bundle cache commands
    '''

    def __init__(self, parent):
        self._parent = parent

    def list(self):
        '''
        List bundles in the cache
        '''
        bundles_directory = self._parent._bundles_directory()
        cache = Cache(bundles_directory)
        return GeneratorWithData(cache.list(),
                text_format=lambda nd: "{id}{name}@{version}{description}".format(
                    id=nd['id'],
                    name=('(%s)' % nd['name'] if nd.get('name') else ''),
                    version=nd.get('version'),
                    description=(' - %s' % (nd.get('description') or nd.get('error'))) if
                    nd.get('description') or nd.get('error') else ''),
                columns=(lambda nd: nd['id'],
                         lambda nd: nd['version'],
                         lambda nd: nd.get('name'),
                         lambda nd: nd.get('description'),
                         lambda nd: nd.get('error', '')),
                default_columns=('ID', 'Version'),
                header=("ID", "Version", "Name", "Description", "Error"))


class OWMBundle(object):
    '''
    Bundle commands
    '''

    remote = SubCommand(OWMBundleRemote)
    cache = SubCommand(OWMBundleCache)

    def __init__(self, parent):
        self._parent = parent
        self._loaders = []

    def fetch(self, bundle_id, bundle_version=None):
        '''
        Retrieve a bundle by id from a remote and put it in the local bundle index and
        cache

        Parameters
        ----------
        bundle_id : str
            The id of the bundle to retrieve.
        bundle_version : int
            The version of the bundle to retrieve. optional
        '''
        f = Fetcher(self._bundles_directory(), self._retrieve_remotes())
        try:
            f.fetch(bundle_id, bundle_version)
        except _NoBundleLoader as e:
            raise NoBundleLoader(e.bundle_id, e.bundle_version)

    def _bundles_directory(self):
        return p(self._parent.userdir, 'bundles')

    def load(self, input_file_name):
        '''
        Load a bundle from a file and register it into the project

        Parameters
        ----------
        input_file_name : str
            The source file of the bundle
        '''
        Unarchiver(bundles_directory=self._bundles_directory()).unpack(input_file_name)

    def save(self, bundle_id, output):
        '''
        Write a bundle to a file

        Writing the bundle to a file writes the bundle descriptor, constituent graphs, and
        attached files to an archive. The bundle can be in the local bundle repository, a
        remote, or registered in the project.

        Parameters
        ----------
        bundle_id : str
            The bundle to save
        output : str
            The target file
        '''

    def install(self, bundle):
        '''
        Install the bundle to the local bundle repository for use across projects on the
        same machine

        Parameters
        ----------
        bundle : str
            ID of the bundle to install or path to the bundle descriptor
        '''
        descriptor_fname = self._get_bundle_descr_fname(bundle)
        if not descriptor_fname:
            descriptor_fname = bundle
        not_known_id = descriptor_fname == bundle
        try:
            descr = self._load_descriptor(descriptor_fname)
        except (OSError, IOError) as e:
            # XXX: Avoiding specialized exception types for Python 2 compat
            if e.errno == 2:  # FileNotFound
                raise GenericUserError('Could not find bundle descriptor with {} {}'.format(
                    'file name' if not_known_id else 'ID',
                    bundle
                ))
            if e.errno == 21:  # IsADirectoryError
                raise GenericUserError('A bundle descriptor is a file, but we were given'
                    ' a directory for {}'.format(bundle))

            raise GenericUserError('Error recovering bundle descriptor with {} {}'.format(
                'file name' if not_known_id else 'ID',
                bundle
            ))

        if not descr:
            raise GenericUserError('Could not find bundle with id {}'.format(bundle))

        imports_ctx = self._parent._conf(IMPORTS_CONTEXT_KEY, None)
        default_ctx = self._parent._conf(DEFAULT_CONTEXT_KEY, None)
        bi = Installer(self._parent.basedir,
                       self._bundles_directory(),
                       self._parent.rdf,
                       imports_ctx=imports_ctx,
                       default_ctx=default_ctx)
        return bi.install(descr)

    def register(self, descriptor):
        '''
        Register a bundle within the project

        Registering a bundle adds it to project configuration and records where the
        descriptor file is within the project's working tree. If the descriptor file moves
        it must be re-registered at the new location.

        Parameters
        ----------
        descriptor : str
            Descriptor file for the bundle
        '''
        descriptor = abspath(descriptor)
        descr = self._load_descriptor(descriptor)
        self._register_bundle(descr, descriptor)

    def _load_descriptor(self, fname):
        with open(fname, 'r') as f:
            return self._parse_descriptor(f)

    def _parse_descriptor(self, fh):
        return Descriptor.make(yaml.full_load(fh))

    def _register_bundle(self, descr, file_name):
        try:
            with open(p(self._parent.owmdir, 'bundles'), 'r') as f:
                lines = f.readlines()
        except OSError:
            lines = []

        with open(p(self._parent.owmdir, 'bundles'), 'w') as f:
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                idx_id, fn = line.split(' ', 1)
                if idx_id == descr.id:
                    continue
                print(line, file=f)
            print('{descr.id} {file_name}\n'.format(**vars()), file=f)

    def _get_bundle_descr_fname(self, bundle_id):
        with open(p(self._parent.owmdir, 'bundles'), 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                idx_id, fn = line.split(' ', 1)
                if bundle_id == idx_id:
                    return fn

    def deregister(self, bundle_id):
        '''
        Remove a bundle from the project

        Parameters
        ----------
        bundle_id : str
            The id of the bundle to deregister
        '''
        try:
            with open(p(self._parent.owmdir, 'bundles'), 'r') as f:
                lines = f.readlines()
        except OSError:
            lines = []

        with open(p(self._parent.owmdir, 'bundles'), 'w') as f:
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                idx_id, fn = line.split(' ', 1)
                if idx_id == bundle_id:
                    continue
                print(line, file=f)

    def deploy(self, bundle_id, remotes=None):
        '''
        Deploys a bundle to a remote. The target remotes come from project and user
        settings or, if provided, the parameters

        Parameters
        ----------
        bundle_id : str
            ID of the bundle to deploy
        remotes : str
            Names of the remotes to deploy to. optional.
        '''

    def checkout(self, bundle_id):
        '''
        Switch to the named bundle

        Parameters
        ----------
        bundle_id : str
            ID of the bundle to switch to
        '''

    def list(self):
        '''
        List registered bundles in the current project.

        To list bundles within the local repo or a remote repo, use the `repo query`
        sub-command.
        '''
        def helper():
            with open(p(self._parent.owmdir, 'bundles'), 'r') as index_fh:
                for line in index_fh:
                    if not line.strip():
                        continue
                    bundle_id, file_name = line.strip().split(' ', 1)
                    try:
                        with open(file_name, 'r') as bundle_fh:
                            descr = self._parse_descriptor(bundle_fh)
                            yield {'name': bundle_id, 'description': descr.description or ""}
                    except (IOError, OSError):
                        # This is at debug level since the error should be expressed well
                        # enough by the response, but we still want to show it eventually
                        L.debug("Cannot read bundle descriptor at"
                                " '{}'".format(file_name),
                                exc_info=True)
                        yield {'name': bundle_id, 'error': "ERROR: Cannot read bundle descriptor at '{}'".format(
                            relpath(file_name)
                            )}
        return GeneratorWithData(helper(),
                text_format=lambda nd: "{name} - {description}".format(name=nd['name'],
                    description=(nd.get('description') or nd.get('error'))),
                columns=(lambda nd: nd['name'],
                         lambda nd: nd.get('description'),
                         lambda nd: nd.get('error')),
                header=("Name", "Description", "Error"))

    def _retrieve_remotes(self):
        return retrieve_remotes(self._parent.owmdir)


class NoBundleLoader(GenericUserError):
    '''
    Thrown when a loader can't be found for a loader
    '''

    def __init__(self, bundle_id, bundle_version=None):
        super(NoBundleLoader, self).__init__(
            'No loader could be found for "%s"%s' % (bundle_id,
                (' at version ' + str(bundle_version)) if bundle_version is not None else ''))


class BundleNotFound(GenericUserError):
    '''
    Thrown when a bundle cannot be found with the requested name and ID
    '''

    def __init__(self, bundle_id, bundle_version=None):
        super(BundleNotFound, self).__init__(
            'The requested bundle could not be loaded "%s"%s' % (bundle_id,
                (' at version ' + bundle_version) if bundle_version is not None else ''))
