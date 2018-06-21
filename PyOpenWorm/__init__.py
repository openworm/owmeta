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
__version__ = '0.8.2'
__author__ = 'Stephen Larson'

import sys
import os

BASE_SCHEMA_URL = 'http://openworm.org/schema'

# The c extensions are incompatible with our code...
os.environ['WRAPT_DISABLE_EXTENSIONS'] = '1'

from .configure import Configureable
from .context import Context
import yarom
from yarom.mapper import Mapper
from PyOpenWorm.import_override import Overrider

__import__('__main__').connected = False
__all__ = [
    "get_data",
    "loadConfig",
    "loadData",
    "disconnect",
    "connect",
    "config",
    ]

# Base class names is empty because we won't be adding any objects to the
# context automatically
mapper = Mapper(base_class_names=('PyOpenWorm.dataObject.DataObject',
                                  'PyOpenWorm.simpleProperty.RealSimpleProperty'))
# An "empty" context, that serves as the default when no context is defined
DEF_CTX = Context(mapper=mapper)

RDF_CONTEXT = Context(ident='http://www.w3.org/1999/02/22-rdf-syntax-ns',
                      base_namespace='http://www.w3.org/1999/02/22-rdf-syntax-ns#',
                      mapper=mapper)

RDFS_CONTEXT = Context(ident='http://www.w3.org/2000/01/rdf-schema',
                       imported=(RDF_CONTEXT,),
                       base_namespace='http://www.w3.org/2000/01/rdf-schema#',
                       mapper=mapper)


BASE_CONTEXT = Context(imported=(RDFS_CONTEXT,),
                       ident=BASE_SCHEMA_URL,
                       base_namespace=BASE_SCHEMA_URL + '#',
                       mapper=mapper)

SCI_CTX = Context(imported=(BASE_CONTEXT,),
                  ident=BASE_SCHEMA_URL + '/sci',
                  base_namespace=BASE_SCHEMA_URL + '/sci#',
                  mapper=mapper)

SCI_BIO_CTX = Context(imported=(SCI_CTX,),
                      ident=BASE_SCHEMA_URL + '/sci/bio',
                      base_namespace=BASE_SCHEMA_URL + '/sci/bio#',
                      mapper=mapper)

CONTEXT = Context(imported=(SCI_BIO_CTX,),
                  ident=BASE_SCHEMA_URL + '/bio',
                  base_namespace=BASE_SCHEMA_URL + '/bio#',
                  mapper=mapper)

yarom.MAPPER = CONTEXT.mapper
overrider = Overrider(yarom.MAPPER)
overrider.wrap_import()
overrider.install_excepthook()


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


def loadConfig(f):
    """ Load configuration for the module. """
    from .data import Data
    Configureable.default = Data.open(f)
    return Configureable.default


def disconnect(c=False):
    """ Close the database. """

    m = __import__('__main__')
    if not m.connected:
        return

    if not c:
        c = Configureable.default

    if c:
        c.closeDatabase()

    from .dataObject import disconnect as DODisconnect
    from .dataObject import PropertyTypes
    DODisconnect()
    assert(len(PropertyTypes) == 0)

    m.connected = False


def loadData(
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
            db_file_name = config('rdf.store.conf')
            if os.path.isfile(db_file_name):
                data_file_time = os.path.getmtime(data)
                db_file_time = os.path.getmtime(config('rdf.store_conf'))
                if data_file_time < db_file_time:
                    return
        except Exception as e:
            logging.exception("Failed to determine if the serialized data file is older than the binary database."
                              " The data file will be reloaded. Reason: {}".format(e.message))
    sys.stderr.write(
        "[PyOpenWorm] Loading data into the graph; this may take several minutes!!\n")
    config('rdf.graph').parse(data, format=dataFormat)


def connect(configFile=False,
            conf=False,
            do_logging=False,
            data=False,
            dataFormat='n3'):
    """
     Load desired configuration and open the database

    :param configFile: (Optional) The configuration file for PyOpenWorm
    :param conf: (Optional) If true, initializes a data object with the PyOpenWorm configuration
    :param do_logging: (Optional) If true, turn on debug level logging
    :param data: (Optional) If provided, specify the file to load into the library
    :param dataFormat: (Optional) If provided, specify the file format to load into the library. Currently n3 is supported
    """
    import logging
    import atexit
    from .data import Data
    m = __import__('__main__')
    if m.connected:
        print ("PyOpenWorm already connected")
        return

    if do_logging:
        logging.basicConfig(level=logging.DEBUG)

    if conf:
        if not isinstance(conf, Data):
            # Initializes a Data object with
            # the Configureable.conf
            conf = Data(conf)
    elif configFile:
        conf = loadConfig(configFile)
    else:
        conf = Data({
            "rdf.source": "ZODB",
            "rdf.store": "ZODB",
            "rdf.store_conf": get_data('worm.db'),
            "rdf.upload_block_statement_count": 50
        })

    Configureable.default = conf
    conf.openDatabase()
    logging.getLogger('PyOpenWorm').info("Connected to database")

    atexit.register(disconnect)

    m.connected = True
    if data:
        loadData(data, dataFormat)
