# -*- coding: utf-8 -*-

"""
.. _owm_module:

owmeta
======

OpenWorm Unified Data Abstract Layer.

An introduction to owmeta can be found in the README on our
`Github page <https://github.com/openworm/owmeta>`_.
"""

from __future__ import print_function
__version__ = '0.12.1'
__author__ = 'OpenWorm.org authors and contributors'

import logging

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())

BASE_SCHEMA_URL = 'http://schema.openworm.org/2020/07/sci'
BASE_BIO_SCHEMA_URL = 'http://schema.openworm.org/2020/07/sci/bio'
BASE_DATA_URL = 'http://data.openworm.org/sci'
BASE_BIO_DATA_URL = 'http://data.openworm.org/sci/bio'

from owmeta_core import BASE_CONTEXT
from owmeta_core.context import Context, ClassContext

DEF_CTX = Context()

SCI_CTX = ClassContext(imported=(BASE_CONTEXT,),
                      ident=BASE_SCHEMA_URL,
                      base_namespace=BASE_SCHEMA_URL + '#')

CONTEXT = ClassContext(imported=(SCI_CTX,),
                  ident=BASE_BIO_SCHEMA_URL,
                  base_namespace=BASE_BIO_SCHEMA_URL + '#')
