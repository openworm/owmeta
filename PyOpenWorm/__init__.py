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

Relationship objects are key to the `Evidence class <#evidence>`_ for sourcing statements.
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
"""

__version__ = '0.0.1-alpha'
__author__ = 'Stephen Larson'

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

config = Configureable.default

def useTestConfig():
    cfg = {
        "connectomecsv" : "https://raw.github.com/openworm/data-viz/master/HivePlots/connectome.csv",
        "neuronscsv" : "https://raw.github.com/openworm/data-viz/master/HivePlots/neurons.csv",
        "sqldb" : "/home/markw/work/openworm/PyOpenWorm/db/celegans.db",
        "rdf.source" : "sparql_endpoint",
        "rdf.store_conf" : ["http://107.170.133.175:8080/openrdf-sesame/repositories/test","http://107.170.133.175:8080/openrdf-sesame/repositories/test/statements"],
        "user.email" : "jerry@cn.com",
        "test_variable" : "test_value"
    }
    for x in cfg:
        Configureable.default[x] = cfg[x]
    Configureable.default = Data(Configureable.default)

def loadConfig(f):
    """ Load configuration for the module """
    Configureable.default = Data.open(f)

def disconnect():
    """ Close the database """
    Configureable.default.closeDatabase()

def connect(configFile=False,conf=False,testConfig=False,do_logging=False):
    """ Load desired configuration and open the database """

    import logging
    import atexit
    if do_logging:
        logging.basicConfig(level=logging.DEBUG)

    if conf:
        Configureable.default = conf
    elif configFile:
        loadConfig(configFile)
    elif testConfig:
        useTestConfig()
    else:
        Configureable.default = Data()

    Configureable.default.openDatabase()
    logging.info("Connected to database")
    atexit.register(disconnect)
