'''
Bundle commands
'''
from __future__ import print_function
import logging
from os.path import join as p, abspath, relpath
from ..command_util import GenericUserError, GeneratorWithData
from ..bundle import Descriptor


L = logging.getLogger(__name__)


class OWMBundle(object):
    '''
    Bundle commands
    '''

    def __init__(self, parent):
        self._parent = parent

    def fetch(self, bundle_name):
        '''
        Retrieve a bundle by name from a remote and put it in the local bundle index and
        cache

        Parameters
        ----------
        bundle_name : str
            The name of the bundle to retrieve
        '''
        self._load(bundle_name)

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
        # Enumerate the contexts
        for c in self._select_contexts(descr):
            print(c)
        # Serialize and hash the contexts
        # Select the files
        # Hash the file contents

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
        import yaml
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

    def _select_contexts(self, descr):
        for graph in self._parent._data_ctx.stored.rdf_graph().contexts():
            ctx = graph.identifier
            for inc in descr.includes:
                if inc(ctx):
                    yield ctx
                    break

            for pat in descr.patterns:
                if pat(ctx):
                    yield ctx
                    break

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
                    except (IOError, OSError, FileNotFoundError):
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

    def _load(self, bundle_name):
        loader = self._get_bundle_loader(bundle_name)
        if not loader:
            raise NoBundleLoader(bundle_name)

        bundle = loader(bundle_name)

    def _get_bundle_loader(self, bundle_name):
        pass


class NoBundleLoader(GenericUserError):
    '''
    Thrown when a loader can't be found for a loader
    '''

    def __init__(self, bundle_name):
        super(NoBundleLoader, self).__init__(
            'No loader could be found for "%s"' % bundle_name)
