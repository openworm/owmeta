# -*- coding: utf-8 -*-
#

from setuptools import setup
import os
import sys


long_description = """
owmeta
======

A unified, simple data access library in Python for data, facts, and models of
*C. elegans* anatomy for the `OpenWorm project <http://www.openworm.org>`_

What does it do?
----------------

Enables a simple Python API for asking various questions about the cells of the
*C. elegans*, enabling the sharing of data about *C. elegans* for the purpose
of building a `data-to-model pipeline <http://docs.openworm.org/en/latest/projects>`_
for the OpenWorm project. In addition, it is a repository for various iterations
of inferred / predicted data about *C. elegans*. Uncontroversial facts and
inferred information are distinguished through the use of explicit Evidence
references.
"""


for line in open('owmeta/__init__.py'):
    if line.startswith("__version__"):
        version = line.split("=")[1].strip()[1:-1]

package_data_excludes = ['.*', '*.bkp', '~*']


def excludes(base):
    res = []
    for x in package_data_excludes:
        res.append(os.path.join(base, x))
    return res


def py2_only(*args):
    return [x + ' ; python_version < "3.0"' for x in args]


setup(
    name='owmeta',
    zip_safe=False,
    setup_requires=['pytest-runner'],
    tests_require=[
        'pytest<5.0.0 ; python_version < "3.0"',
        'pytest>=3.4.0 ; python_version >= "3.0"',
        'pytest-cov>=2.5.1',
        'discover==0.4.0',
        'rdflib-sqlalchemy',
        'mock==2.0.0 ; python_version < "3.0"',
        'pytest-parallel ; python_version >= "3.0"'
    ],
    install_requires=[
        'bibtexparser~=1.1.0',
        'BTrees==4.0.8',
        'gitpython>=2.1.1',
        'lazy-object-proxy==1.2.1',
        'libneuroml',
        'numpydoc>=0.7.0',
        'persistent==4.0.8',
        'Pint==0.8.1',
        'pow-store-zodb==0.0.7',
        'rdflib>=4.1.2',
        'six~=1.10',
        'tqdm~=4.23',
        'termcolor==1.1.0',
        'transaction>=1.4.4',
        'wrapt~=1.11.1',
        'yarom~=0.12.0',
        'zc.lockfile',
        'ZConfig==3.0.4',
        'zdaemon==4.0.0',
        'zodb==4.1.0',
        'rdflib-sqlalchemy',
        'pyyaml',
    ] + py2_only('zodbpickle==1.0',
        'Sphinx<1.8.4',
        'backports.tempfile==1.0',
        'scandir',
        'docutils<0.15'),
    extras_require={
        # SQL source support
        'mysql_source_mysql_connector': [
            'mysql-connector-python'
        ],
        'mysql_source_mysqlclient': [
            'mysqlclient'
        ],
        'postgres_source_psycopg': [
            'psycopg2'
        ],
        'postgres_source_pg8000': [
            'pg8000'
        ]
    },
    version=version,
    packages=['owmeta',
              'owmeta.data_trans',
              'owmeta.commands'],
    author='OpenWorm.org authors and contributors',
    author_email='info@openworm.org',
    description='A Python library for working with OpenWorm data and models',
    long_description=long_description,
    license='MIT',
    url='http://owmeta.readthedocs.org/en/latest/',
    download_url='https://github.com/openworm/owmeta/archive/master.zip',
    entry_points={'console_scripts': ['owm = owmeta.cli:main']},
    package_data={'owmeta': ['default.conf']},
    classifiers=[
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering'
    ]
)
