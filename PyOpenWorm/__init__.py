# -*- coding: utf-8 -*-

"""
PyOpenWorm
==========

OpenWorm Unified Data Abstract Layer.

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

Relationship objects are key to the `Evidence class <#PyOpenWorm.Evidence>`_ for sourcing statements.
Relationships can themselves be members in a relationship, allowing for fairly complex hierarchical statements to
be made about entities.

Notes:

- Of course, when these methods communicate with an external database, they may fail due to the database being
  unavailable and the user should be notified if a connection cannot be established in a reasonable time. Also, some
  objects are created by querying the database; these may be made out-of-date in that case.

- ``a : {x_0,...,x_n}`` means ``a`` could have the value of any one of ``x_0`` through ``x_n``

Classes
-------

.. autoclass:: Network
.. autoclass:: Neuron
.. autoclass:: Worm
.. autoclass:: Muscle
.. autoclass:: Evidence
.. autoclass:: Connection
.. autoclass:: Relationship
.. automodule:: PyOpenWorm.dataObject
.. autoclass:: Property
.. automodule:: PyOpenWorm.data
.. automodule:: PyOpenWorm.cell
.. automodule:: PyOpenWorm.configure
"""

__version__ = '0.0.1-alpha'
__author__ = 'Stephen Larson'

from .configure import Configure,Configureable,ConfigValue,BadConf
from .data import Data,DataUser,propertyTypes
from .mapper import DataObjectMapper
from .quantity import Quantity

__import__('__main__').connected = False

def config():
    return Configureable.conf

def useTestConfig():
    cfg = {
    "connectomecsv" : "https://raw.github.com/openworm/data-viz/master/HivePlots/connectome.csv",
    "neuronscsv" : "https://raw.github.com/openworm/data-viz/master/HivePlots/neurons.csv",
    "sqldb" : "/home/markw/work/openworm/PyOpenWorm/db/celegans.db",
    "rdf.source" : "default",
    "rdf.store" : "Sleepycat",
    "rdf.store_conf" : "worm.db",
    "user.email" : "jerry@cn.com",
    "rdf.upload_block_statement_count" : 50,
    "test_variable" : "test_value"
    }

    for x in cfg:
        Configureable.conf[x] = cfg[x]
    Configureable.conf = Data(Configureable.conf)

def loadConfig(f):
    """ Load configuration for the module """
    Configureable.conf = Data.open(f)

def disconnect(c=False):
    """ Close the database """
    m = __import__('__main__')
    if not m.connected:
        return
    if c == False:
        c = Configureable.conf

    if c != False:
        c.closeDatabase()
    m.connected = False

def connect(configFile=False,
        conf=False,
        testConfig=False,
        do_logging=False):
    """ Load desired configuration and open the database """
    import logging
    import atexit
    import sys
    m = __import__('__main__')
    if m.connected == True:
        print "PyOpenWorm already connected"
        return

    if do_logging:
        logging.basicConfig(level=logging.DEBUG)

    if conf:
        Configureable.conf = conf
        if not isinstance(conf, Data):
            d = Data()
            Configureable.conf = d
    elif configFile:
        loadConfig(configFile)
    elif testConfig:
        useTestConfig()
    else:
        Configureable.conf = Data()

    Configureable.conf.openDatabase()
    logging.info("Connected to database")

    # have to register the right one to disconnect...
    c = Configureable.conf
    atexit.register(disconnect)
    Configureable._lh = hash(Configureable.conf)
    from .dataObject import DataObject, Property, SimpleProperty
    from .cell import Cell
    from .network import Network
    from .neuron import Neuron
    from .worm import Worm
    from .relationship import Relationship
    from .evidence import Evidence,EvidenceError
    from .muscle import Muscle
    from .connection import Connection

    # Not a dataobject, but depends on some of them
    from .my_neuroml import NeuroML
    DataObjectMapper.setUpDB()
