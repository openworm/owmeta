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

__version__ = '0.0.1'
__author__ = 'Stephen Larson'

from .configure import Configure,Configureable,ConfigValue,DefaultConfig
from .data import Data,DataUser,propertyTypes
from .network import Network
from .neuron import Neuron
from .worm import Worm
from .muscle import Muscle
