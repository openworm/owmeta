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

__version__ = '0.5.0-alpha'
__author__ = 'Stephen Larson'

import traceback
import sys
from .configure import Configure,Configureable,ConfigValue,BadConf
from .data import Data,DataUser,propertyTypes
from .dataObject import *
from .cell import Cell
from .network import Network
from .neuron import Neuron
from .worm import Worm
from .relationship import Relationship
from .evidence import Evidence,EvidenceError
from .muscle import Muscle
from .quantity import Quantity
from .my_neuroml import NeuroML
from .connection import Connection

__import__('__main__').connected = False

def config(key=None):
    """ Gets the main configuration for the whole PyOpenWorm library.
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

    if c == False:
        c = Configureable.conf
    if c != False:
        c.closeDatabase()
    m.connected = False


def loadData(data='OpenWormData/WormData.n3', dataFormat='n3'):
    """ Load data into the underlying database of this library.
    :param data: (Optional) Specify the file to load into the library
    :param dataFormat: (Optional) Specify the file format to load into the library.  Currently n3 is supported
    :return:
    """
    if data:
        sys.stderr.write("[PyOpenWorm] Loading data into the graph; this may take several minutes!!")
        config()['rdf.graph'].parse(data, format=dataFormat)

def connect(configFile='PyOpenWorm/default.conf',
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
    :return:
    """
    import logging
    import atexit
    m = __import__('__main__')
    if m.connected == True:
        print "PyOpenWorm already connected"
        return

    if do_logging:
        logging.basicConfig(level=logging.DEBUG)

    if conf:
        Configureable.conf = conf
        if not isinstance(conf, Data):
            # Initializes a Data object with
            # the Configureable.conf
            Configureable.conf = Data()
    elif configFile:
        loadConfig(configFile)
    else:
        try:
            from pkg_resources import Requirement, resource_filename
            filename = resource_filename(Requirement.parse("PyOpenWorm"),"PyOpenWorm/default.conf")
            Configureable.conf = Data.open(filename)
        except:
            logging.info("Couldn't load default configuration")
            traceback.print_exc()
            Configureable.conf = Data()

    Configureable.conf.openDatabase()
    logging.info("Connected to database")

    # have to register the right one to disconnect...
    atexit.register(disconnect)

    # This takes all the classes that we want to store metadata in the database
    #  and lets our data handling system know about them.
    #  Should add new classes here if they need to be tracked!
    DataObject.register()
    Cell.register()
    Network.register()
    Neuron.register()
    Worm.register()
    Evidence.register()
    Muscle.register()
    Connection.register()
    SimpleProperty.register()
    Property.register()
    Relationship.register()

    m.connected = True
    if data:
        loadData(data, dataFormat)
