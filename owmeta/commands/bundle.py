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
from ..context import DATA_CONTEXT_KEY, IMPORTS_CONTEXT_KEY
from ..command_util import GenericUserError, GeneratorWithData, SubCommand
from ..bundle import (Descriptor,
                      Installer,
                      HTTPBundleLoader,
                      URLConfig,
                      Remote,
                      bundle_directory)
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
                L.warn('Could not crerate directory for storage of remote configurations', exc_info=True)
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


class OWMBundle(object):
    '''
    Bundle commands
    '''

    remote = SubCommand(OWMBundleRemote)

    def __init__(self, parent):
        self._parent = parent
        self._loaders = []

        self._loader_classes = [
            HTTPBundleLoader
        ]
        ''' Priority-sorted list of bundle loader classes '''

    def fetch(self, bundle_name, bundle_version=None):
        '''
        Retrieve a bundle by name from a remote and put it in the local bundle index and
        cache

        Parameters
        ----------
        bundle_name : str
            The name of the bundle to retrieve. The name may include the version number.
        bundle_version : int
            The version of the bundle to retrieve. optional
        '''
        loaders = self._get_bundle_loaders(bundle_name, bundle_version)

        for loader in loaders:
            try:
                if bundle_version is None:
                    versions = loader.bundle_versions(bundle_name)
                    if not versions:
                        raise BundleNotFound(bundle_name, bundle_version)
                    bundle_version = max(versions)
                loader.base_directory = bundle_directory(p(self._parent.userdir, 'bundles'),
                        bundle_name, bundle_version)
                try:
                    loader(bundle_name, bundle_version)
                finally:
                    loader.base_directory = None
                break
            except Exception:
                L.warn("Failed to load bundle %s with %s", bundle_name, loader, exc_info=True)
        else: # no break
            raise NoBundleLoader(bundle_name)

    def load(self, input_file_name):
        '''
        Load a bundle from a file and register it into the project

        Parameters
        ----------
        input_file_name : str
            The source file of the bundle
        '''

    def save(self, bundle_name, output):
        '''
        Write a bundle to a file

        Writing the bundle to a file writes the bundle descriptor, constituent graphs, and
        attached files to an archive. The bundle can be in the local bundle repository, a
        remote, or registered in the project.

        Parameters
        ----------
        bundle_name : str
            The bundle to save
        output : str
            The target file
        '''

    def install(self, bundle_name):
        '''
        Install the bundle to the local bundle repository for use across projects on the
        same machine

        Parameters
        ----------
        bundle_name : str
            Name of the bundle to install
        '''
        descr = self._load_descriptor_by_name(bundle_name)
        if not descr:
            descr = self._load_descriptor(bundle_name)
        if not descr:
            raise GenericUserError('Could not find bundle with name {}'.format(bundle_name))
        imports_ctx = self._parent._conf(IMPORTS_CONTEXT_KEY, None)
        data_ctx = self._parent._conf(DATA_CONTEXT_KEY, None)
        bi = Installer(self._parent.basedir,
                       p(self._parent.userdir, 'bundles'),
                       self._parent.rdf,
                       imports_ctx=imports_ctx,
                       data_ctx=data_ctx)
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

    def _load_descriptor_by_name(self, bundle_name):
        return self._load_descriptor(self._get_bundle_fname(bundle_name))

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
                name, fn = line.split(' ', 1)
                if name == descr.name:
                    continue
                print(line, file=f)
            print('{descr.name} {file_name}\n'.format(**vars()), file=f)

    def _get_bundle_fname(self, name):
        with open(p(self._parent.owmdir, 'bundles'), 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                idx_name, fn = line.split(' ', 1)
                if name == idx_name:
                    return fn

    def deregister(self, bundle_name):
        '''
        Remove a bundle from the project

        Parameters
        ----------
        bundle_name : str
            The name of the bundle to deregister
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
                name, fn = line.split(' ', 1)
                if name == bundle_name:
                    continue
                print(line, file=f)

    def deploy(self, bundle_name, remotes=None):
        '''
        Deploys a bundle to a remote. The target remotes come from project and user
        settings or, if provided, the parameters

        Parameters
        ----------
        bundle_name : str
            Name of the bundle to deploy
        remotes : str
            Names of the remotes to deploy to
        '''

    def checkout(self, bundle_name):
        '''
        Switch to the named bundle

        Parameters
        ----------
        bundle_name : str
            Name of the bundle to switch to
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
                    name, file_name = line.strip().split(' ', 1)
                    try:
                        with open(file_name, 'r') as bundle_fh:
                            descr = self._parse_descriptor(bundle_fh)
                            yield {'name': name, 'description': descr.description or ""}
                    except (IOError, OSError):
                        # This is at debug level since the error should be expressed well
                        # enough by the response, but we still want to show it eventually
                        L.debug("Cannot read bundle descriptor at"
                                " '{}'".format(file_name),
                                exc_info=True)
                        yield {'name': name, 'error': "ERROR: Cannot read bundle descriptor at '{}'".format(
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
        remotes_dir = p(self._parent.owmdir, 'remotes')
        for r in listdir(remotes_dir):
            if r.endswith('.remote'):
                with open(p(remotes_dir, r)) as inp:
                    try:
                        yield Remote.read(inp)
                    except Exception:
                        L.warning('Unable to read remote %s', r, exc_info=True)

    def _get_bundle_loaders(self, bundle_name, bundle_version):
        for rem in self._retrieve_remotes():
            for loader in rem.generate_loaders(self._loader_classes):
                if loader.can_load(bundle_name, bundle_version):
                    yield loader


class NoBundleLoader(GenericUserError):
    '''
    Thrown when a loader can't be found for a loader
    '''

    def __init__(self, bundle_name, bundle_version=None):
        super(NoBundleLoader, self).__init__(
            'No loader could be found for "%s"%s' % (bundle_name,
                (' at version ' + bundle_version) if bundle_version is not None else ''))


class BundleNotFound(GenericUserError):
    '''
    Thrown when a bundle cannot be found with the requested name and ID
    '''

    def __init__(self, bundle_name, bundle_version=None):
        super(BundleNotFound, self).__init__(
            'The requested bundle could not be loaded "%s"%s' % (bundle_name,
                (' at version ' + bundle_version) if bundle_version is not None else ''))
