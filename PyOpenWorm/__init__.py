# -*- coding: utf-8 -*-

"""
PyOpenWorm
==========

OpenWorm Unified Data Abstract Layer.

An introduction to PyOpenWorm can be found in the README on our `Github page <https://github.com/openworm/PyOpenWorm/tree/alpha0.5#readme>`_.

Most statements correspond to some action on the database.
Some of these actions may be complex, but intuitively ``a.B()``, the Query form,
will query against the database for the value or values that are related to ``a`` through ``B``;
on the other hand, ``a.B(c)``, the Update form, will add a statement to the database that ``a``
relates to ``c`` through ``B``. For the Update form, a Relationship object describing the
relationship stated is returned as a side-effect of the update.

The Update form can also be accessed through the set() method of a Property and the Query form through the get()
method like::

    a.B.set(c)

and::

    a.B.get()

The get() method also allows for parameterizing the query in ways specific to the Property.

Relationship objects are key to the :class:`Evidence class <.Evidence>` for sourcing statements.
Relationships can themselves be members in a relationship, allowing for fairly complex hierarchical statements to
be made about entities.

Notes:

- Of course, when these methods communicate with an external database, they may fail due to the database being
  unavailable and the user should be notified if a connection cannot be established in a reasonable time. Also, some
  objects are created by querying the database; these may be made out-of-date in that case.

- ``a : {x_0,...,x_n}`` means ``a`` could have the value of any one of ``x_0`` through ``x_n``

Classes
-------

.. automodule:: PyOpenWorm.experiment
.. automodule:: PyOpenWorm.channel
.. automodule:: PyOpenWorm.evidence
.. automodule:: PyOpenWorm.network
.. automodule:: PyOpenWorm.neuron
.. automodule:: PyOpenWorm.worm
.. automodule:: PyOpenWorm.muscle
.. automodule:: PyOpenWorm.connection
.. automodule:: PyOpenWorm.relationship
.. automodule:: PyOpenWorm.dataObject
.. automodule:: PyOpenWorm.data
.. automodule:: PyOpenWorm.cell
.. automodule:: PyOpenWorm.configure
"""

from __future__ import print_function
__version__ = '0.7.1'
__author__ = 'Stephen Larson'

import sys
import os

# For re-export
from .configure import Configure, Configureable, ConfigValue, BadConf
from .data import Data, DataUser, propertyTypes
from .dataObject import DataObject
from .pProperty import Property
from .simpleProperty import SimpleProperty
from .cell import Cell
from .network import Network
from .neuron import Neuron
from .worm import Worm
from .relationship import Relationship
from .evidence import Evidence, EvidenceError
from .muscle import Muscle
from .quantity import Quantity
from .my_neuroml import NeuroML
from .connection import Connection
from .experiment import Experiment
from .channel import Channel
from .channelworm import ChannelModel, PatchClampExperiment
from .plot import Plot

__import__('__main__').connected = False
__all__ = [
    "get_data",
    "loadConfig",
    "loadData",
    "disconnect",
    "connect",
    "config",
    "Configure",
    "Configureable",
    "ConfigValue",
    "BadConf",
    "Data",
    "DataObject",
    "DataUser",
    "propertyTypes",
    "Property",
    "SimpleProperty",
    "Cell",
    "Network",
    "Neuron",
    "Worm",
    "Relationship",
    "EvidenceError",
    "Muscle",
    "Quantity",
    "NeuroML",
    "Connection",
    "Experiment",
    "Channel",
    "ChannelModel",
    "PatchClampExperiment",
    "Plot"]

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
        return Configureable.conf
    else:
        return Configureable.conf[key]


def loadConfig(f):
    """ Load configuration for the module. """
    Configureable.conf = Data.open(f)
    return Configureable.conf


def disconnect(c=False):
    """ Close the database. """

    m = __import__('__main__')
    if not m.connected:
        return

    if not c:
        c = Configureable.conf

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
            logging.exception("Failed to determine if the serialized data file is older than the binary database. The data"
                            " file will be reloaded. Reason: {}".format(e.message))
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
            Configureable.conf = Data(conf)
        else:
            Configureable.conf = conf
    elif configFile:
        loadConfig(configFile)
    else:
        Configureable.conf = Data({
            "connectomecsv" : "OpenWormData/aux_data/connectome.csv",
            "neuronscsv" : "OpenWormData/aux_data/neurons.csv",
            "rdf.source" : "ZODB",
            "rdf.store" : "ZODB",
            "rdf.store_conf" : get_data('worm.db'),
            "user.email" : "jerry@cn.com",
            "rdf.upload_block_statement_count" : 50
        })

    Configureable.conf.openDatabase()
    logging.info("Connected to database")

    # have to register the right one to disconnect...
    atexit.register(disconnect)

    # This takes all the classes that we want to store metadata in the database
    #  and lets our data handling system know about them.
    #  Should add new classes here if they need to be tracked!
    DataObject.register()
    Network.register()
    Cell.register()
    Neuron.register()
    Worm.register()
    Evidence.register()
    Muscle.register()
    Connection.register()
    SimpleProperty.register()
    Property.register()
    Relationship.register()
    Channel.register()
    ChannelModel.register()
    Experiment.register()
    PatchClampExperiment.register()
    Plot.register()

    m.connected = True
    if data:
        loadData(data, dataFormat)
