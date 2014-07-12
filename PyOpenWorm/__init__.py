# -*- coding: utf-8 -*-

"""
PyOpenWorm
==========

OpenWorm Unified Data Abstract Layer.

Classes
-------

.. autoclass:: Network
   :members:
.. autoclass:: Neuron
   :members:
.. autoclass:: Worm
   :members:
.. autoclass:: Muscle
   :members:
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

def useTestConfig(do_logging):
    import logging
    if do_logging:
        logging.basicConfig(level=logging.DEBUG)
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

def connect(conf=False,configFile=False,testConfig=False):
    """ Load desired configuration and open the database """
    if conf:
        Configureable.default = conf
    elif configFile:
        loadConfig(configFile)
    elif testConfig:
        useTestConfig(do_logging=False)
    Configureable.default.openDatabase()
