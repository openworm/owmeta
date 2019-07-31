# -*- coding: utf-8 -*-

"""
.. _pow_module:

PyOpenWorm
==========

OpenWorm Unified Data Abstract Layer.

An introduction to PyOpenWorm can be found in the README on our
`Github page <https://github.com/openworm/PyOpenWorm>`_.

Most statements correspond to some action on the database.
Some of these actions may be complex, but intuitively ``a.B()``, the Query form,
will query against the database for the value or values that are related to ``a`` through ``B``;
on the other hand, ``a.B(c)``, the Update form, will add a statement to the database that ``a``
relates to ``c`` through ``B``. For the Update form, a Statement object describing the
relationship stated is returned as a side-effect of the update.

The Update form can also be accessed through the set() method of a Property and the Query form through the get()
method like::

    a.B.set(c)

and::

    a.B.get()

The get() method also allows for parameterizing the query in ways specific to the Property.

"""

from __future__ import print_function
__version__ = '0.11.1'
__author__ = 'Stephen Larson'

import sys
import os
import logging

LOGGER = logging.getLogger(__name__)

BASE_SCHEMA_URL = 'http://openworm.org/schema'

# The c extensions are incompatible with our code...
os.environ['WRAPT_DISABLE_EXTENSIONS'] = '1'
from .import_override import Overrider
from .module_recorder import ModuleRecorder as MR
from .mapper import Mapper

ImportOverrider = None
ModuleRecorder = None


BASE_MAPPER = Mapper(base_class_names=('PyOpenWorm.dataObject.DataObject',
    'PyOpenWorm.simpleProperty.RealSimpleProperty'))
'''
Handles some of the PyOpenWorm DataObjects regardless of whether there's been any connection. Used by Contexts outside
of a connection.
'''


def install_module_import_wrapper():
    global ImportOverrider
    global ModuleRecorder

    if ImportOverrider is None:
        ModuleRecorder = MR()
        ImportOverrider = Overrider(mapper=ModuleRecorder)
        ImportOverrider.wrap_import()
        ImportOverrider.install_excepthook()
    else:
        LOGGER.info("Import overrider already installed")
    return ImportOverrider


install_module_import_wrapper()
ModuleRecorder.add_listener(BASE_MAPPER)
from .configure import Configureable
from .context import Context
import yarom

__all__ = [
    "get_data",
    "loadConfig",
    "loadData",
    "disconnect",
    "connect",
    "config",
    ]

DEF_CTX = Context()

RDF_CONTEXT = Context(ident='http://www.w3.org/1999/02/22-rdf-syntax-ns',
                      base_namespace='http://www.w3.org/1999/02/22-rdf-syntax-ns#')

RDFS_CONTEXT = Context(ident='http://www.w3.org/2000/01/rdf-schema',
                       imported=(RDF_CONTEXT,),
                       base_namespace='http://www.w3.org/2000/01/rdf-schema#')

BASE_CONTEXT = Context(imported=(RDFS_CONTEXT,),
                       ident=BASE_SCHEMA_URL,
                       base_namespace=BASE_SCHEMA_URL + '#')

SCI_CTX = Context(imported=(BASE_CONTEXT,),
                  ident=BASE_SCHEMA_URL + '/sci',
                  base_namespace=BASE_SCHEMA_URL + '/sci#')

SCI_BIO_CTX = Context(imported=(SCI_CTX,),
                      ident=BASE_SCHEMA_URL + '/sci/bio',
                      base_namespace=BASE_SCHEMA_URL + '/sci/bio#')

CONTEXT = Context(imported=(SCI_BIO_CTX,),
                  ident=BASE_SCHEMA_URL + '/bio',
                  base_namespace=BASE_SCHEMA_URL + '/bio#')


def get_data(path):
    # get a resource from the installed package location

    from sysconfig import get_path
    from pkgutil import get_loader
    from glob import glob
    package_paths = glob(os.path.join(get_path('platlib'), '*'))
    sys.path = package_paths + sys.path
    installed_package_root = os.path.dirname(get_loader('PyOpenWorm').get_filename())
    sys.path = sys.path[len(package_paths):]
    filename = os.path.join(installed_package_root, path)
    return filename


def config(key=None):
    """
    Gets the main configuration for the whole PyOpenWorm library.

    :return: the instance of the Configure class currently operating.
    """
    if key is None:
        return Configureable.default
    else:
        return Configureable.default[key]


class Connection(object):

    def __init__(self, conf):
        self.conf = conf

    def disconnect(self):
        self.conf.closeDatabase()
        ModuleRecorder.remove_listener(self.conf['mapper'])

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.disconnect()


def loadConfig(f):
    """ Load configuration for the module. """
    from .data import Data
    return Data.open(f)


def disconnect(c=False):
    """ Close the database. """
    if c:
        c.disconnect()


def loadData(
        conf,
        data='OpenWormData/WormData.n3',
        dataFormat='n3',
        skipIfNewer=False):
    """
    Load data into the underlying database of this library.

    XXX: This is only guaranteed to work with the ZODB database.

    :param data: (Optional) Specify the file to load into the library
    :param dataFormat: (Optional) Specify the file format to load into the library.  Currently n3 is supported
    :param skipIfNewer: (Optional) Skips loading of data if the database file is newer
                        than the data to be loaded in. This is determined by the modified time on the main
                        database file compared to the modified time on the data file.
    """
    import logging
    if not os.path.isfile(data):
        raise Exception("No such data file: " + data)

    if skipIfNewer:
        try:
            db_file_name = conf['rdf.store.conf']
            if os.path.isfile(db_file_name):
                data_file_time = os.path.getmtime(data)
                db_file_time = os.path.getmtime(conf['rdf.store_conf'])
                if data_file_time < db_file_time:
                    return
        except Exception as e:
            logging.exception("Failed to determine if the serialized data file is older than the binary database."
                              " The data file will be reloaded. Reason: {}".format(e.message))
    sys.stderr.write("[PyOpenWorm] Loading data into the graph; this may take several minutes!!\n")
    conf['rdf.graph'].parse(data, format=dataFormat)


class ConnectionFailError(Exception):
    def __init__(self, cause, *args):
        if args:
            super(ConnectionFailError, self).__init__('PyOpenWorm connection failed: {}. {}'.format(cause, *args))
        else:
            super(ConnectionFailError, self).__init__('PyOpenWorm connection failed: {}'.format(cause))


def connect(configFile=False,
            conf=None,
            do_logging=False,
            data=False,
            dataFormat='n3'):
    """
    Load desired configuration and open the database

    :param configFile: (Optional) The configuration file for PyOpenWorm
    :param conf: (Optional) a configuration object for the connection. Takes precedence over `configFile`
    :param do_logging: (Optional) If true, turn on debug level logging
    :param data: (Optional) specify the file to load into the library
    :param dataFormat: (Optional) file format of `data`. Currently n3 is supported
    """
    import logging
    from .data import Data, ZODBSourceOpenFailError, DatabaseConflict

    if do_logging:
        logging.basicConfig(level=logging.DEBUG)

    if conf:
        if not isinstance(conf, Data):
            conf = Data(conf)
    elif configFile:
        conf = Data.open(configFile)
    else:
        conf = Data({
            "rdf.source": "ZODB",
            "rdf.store": "ZODB",
            "rdf.store_conf": get_data('worm.db'),
            "rdf.upload_block_statement_count": 50
        })

    try:
        conf.init_database()
    except ZODBSourceOpenFailError as e:
        # Special handling for a common user error with pow which, nonetheless,
        # may be encontered when *not* using pow
        if e.openstr.endswith('.pow/worm.db'):
            raise ConnectionFailError(e, 'Perhaps you need to do a `pow clone`?')
        raise ConnectionFailError(e)
    except DatabaseConflict as e:
        raise ConnectionFailError(e, "It looks like a connection is already opened by a living process")
    except Exception as e:
        raise ConnectionFailError(e)

    logging.getLogger('PyOpenWorm').info("Connected to database")

    if data:
        loadData(conf, data, dataFormat)

    # Base class names is empty because we won't be adding any objects to the
    # context automatically
    mapper = Mapper(base_class_names=('PyOpenWorm.dataObject.DataObject',
                                      'PyOpenWorm.simpleProperty.RealSimpleProperty'))
    conf['mapper'] = mapper
    # An "empty" context, that serves as the default when no context is defined

    yarom.MAPPER = mapper

    ModuleRecorder.add_listener(mapper)

    return Connection(conf)
