from os.path import exists, abspath, join as pth_join, dirname
import json


# XXX: How should we handle arguments that apply to many different commands,
# but which don't belong to a sub-command??


class POW(object):

    # Imports, other than those from the standard library, are included in each
    # method separately since, eventually, each method should be independent of
    # the others to the extent that you may even choose not to install
    # dependencies for commands which are not used.  This should permit a
    # generic handler for ImportError wherein a dependency is only installed
    # when needed. This should also reduce load times for each command

    def init(self, store_name='worm.db', config_file='default.conf',
             update_existing_config=False):
        """
        Makes a new graph store

        Parameters
        ----------
        store_name : str
            The base name of the database store
        config_file : str
            The configuration file to use. The configuration file will be
            created if it does not exist. If it *does* exist, the location of
            the database store will, by default, not be changed in that file
        update_existing_config : bool
            If True, updates the existing config file to point to the given
            file for the store configuration
        """
        from PyOpenWorm.data import Data
        store_fname = abspath(store_name)
        if not exists(config_file):
            with open(self._default_config(), 'r') as f:
                default = json.load(f)
                with open(config_file, 'w') as of:
                    default['rdf.store_conf'] = store_fname
                    json.dump(default, of)
        elif update_existing_config:
            with open(config_file, 'r+') as f:
                conf = json.load(f)
                conf['rdf.store_conf'] = store_fname
                f.seek(0)
                json.dump(conf, f)
        dat = Data.open(config_file)

        dat.init_database()

    def clone(self, url=None, store_name='worm.db', config_file='default.conf',
              update_existing_config=False):
        """
        Clone a data store
        Parameters
        ----------
        url : str
            URL of the data store to clone
        """
        # TODO: As a first cut, should download a file at the given URL, verify
        # that it's an RDF serialization, init a git repo, rewrite the
        # serialization as an nquads (setting the clone url as the default
        # context), add the nquads serialization to the git repo, commit to the
        # git repo, do a similar thing to POW::init for initializing the
        # database, add the contents of the nquads to the new database, and,
        # finally, print some summary stats about the newly created database
        # like how many triples, contexts, total size downloaded, etc.

    def translate(self, translator, output_key=None, *data_sources, **named_data_sources):
        """
        Do a translation with the named translator and inputs
        """

    def reconstitute(self, data_source):
        """
        Recreate a data source by executing the chain of translators that went
        into making it.
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
        """

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


class POWSource(object):
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
