'''
Bundle commands
'''
from ..command_util import GenericUserError
from ..bundle import Descriptor


class OWMBundle(object):
    '''
    Bundle commands
    '''

    def __init__(self, parent):
        self._parent = parent

    def fetch(self, bundle_name):
        '''
        Retrieve a bundle by name, possibly from remotes, and put in the local bundle
        repository

        Parameters
        ----------
        bundle_name : str
            The name of the bundle to retrieve
        '''
        self._load(bundle_name)

    def load(self, input_file_name):
        '''
        Load a bundle from a file

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

    def register(self, descriptor):
        '''
        Register a bundle within the project

        Registering a bundle adds it to project configuration and records where the
        descriptor file is within the project's working tree. If the descriptor file moves
        it must be re-registered at the new location.

        Parameters
        ----------
        descriptor : str
            Descriptor For the bundle
        '''
        import yaml
        with open(descriptor) as inp:
            descr = Descriptor.make(yaml.full_load(inp))
        self._select_contexts(descr)

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
