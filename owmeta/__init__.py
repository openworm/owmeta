# -*- coding: utf-8 -*-

"""
.. _owm_module:

owmeta
======

OpenWorm Unified Data Abstract Layer.

An introduction to owmeta can be found in the README on our
`Github page <https://github.com/openworm/owmeta>`_.

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
__version__ = '0.11.3.dev0'
__author__ = 'Stephen Larson'

import sys
import os
import logging

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())

BASE_SCHEMA_URL = 'http://schema.openworm.org/2020/07/sci'
BASE_BIO_SCHEMA_URL = 'http://schema.openworm.org/2020/07/sci/bio'
BASE_DATA_URL = 'http://data.openworm.org/sci'
BASE_BIO_DATA_URL = 'http://data.openworm.org/sci/bio'

from owmeta_core import BASE_CONTEXT
from owmeta_core.configure import Configurable
from owmeta_core.context import Context, ClassContext

__all__ = ["get_data", "Configurable"]

DEF_CTX = Context()

SCI_CTX = ClassContext(imported=(BASE_CONTEXT,),
                      ident=BASE_SCHEMA_URL,
                      base_namespace=BASE_SCHEMA_URL + '#')

CONTEXT = ClassContext(imported=(SCI_CTX,),
                  ident=BASE_BIO_SCHEMA_URL,
                  base_namespace=BASE_BIO_SCHEMA_URL + '#')


def get_data(path):
    # get a resource from the installed package location

    from sysconfig import get_path
    from pkgutil import get_loader
    from glob import glob
    package_paths = glob(os.path.join(get_path('platlib'), '*'))
    sys.path = package_paths + sys.path
    installed_package_root = os.path.dirname(get_loader('owmeta').get_filename())
    sys.path = sys.path[len(package_paths):]
    filename = os.path.join(installed_package_root, path)
    return filename
