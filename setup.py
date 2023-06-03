# -*- coding: utf-8 -*-
#

from setuptools import setup


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


setup(
    name='owmeta',
    zip_safe=False,
    install_requires=[
        'owmeta-core>=0.14.0.dev0',
        'bibtexparser~=1.1.0',
        'libneuroml',
        'rdflib>=4.1.2',
        'six~=1.10',
        'requests',
    ],
    version=version,
    packages=['owmeta',
              'owmeta.data_trans',
              'owmeta.commands'],
    author='OpenWorm.org authors and contributors',
    author_email='info@openworm.org',
    description='A Python library for working with OpenWorm data and models',
    long_description=long_description,
    license='MIT',
    url='https://owmeta.readthedocs.io/en/latest/',
    download_url='https://github.com/openworm/owmeta/archive/master.zip',
    entry_points={
        'owmeta_core.commands': [
            'evidence = owmeta.command:OWMEvidence',
            'cell = owmeta.commands.biology:CellCmd',
        ],
        'owmeta_core.cli_hints': 'hints = owmeta.cli_hints:CLI_HINTS',
    },
    classifiers=[
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Scientific/Engineering'
    ]
)
