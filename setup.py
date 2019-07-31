# -*- coding: utf-8 -*-
#

from setuptools import setup
import os
import sys


long_description = """
PyOpenWorm
===========

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


for line in open('PyOpenWorm/__init__.py'):
    if line.startswith("__version__"):
        version = line.split("=")[1].strip()[1:-1]

package_data_excludes = ['.*', '*.bkp', '~*']

PY2 = sys.version_info.major == 2
PY3 = sys.version_info.major == 3
PY34 = PY3 and sys.version_info.minor == 4


def excludes(base):
    res = []
    for x in package_data_excludes:
        res.append(os.path.join(base, x))
    return res


setup(
    name='PyOpenWorm',
    zip_safe=False,
    setup_requires=['pytest-runner'],
    tests_require=[
        'pytest>=3.4.0',
        'pytest-cov>=2.5.1',
        'discover==0.4.0',
    ] + (['mock==2.0.0'] if PY2 else [])
      + (['pytest-parallel'] if PY3 else []),
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
        'tqdm~=4.23.4',
        'termcolor==1.1.0',
        'transaction>=1.4.4',
        'wrapt==1.10.11',
        'yarom>=0.11.0',
        'zc.lockfile==1.1.0',
        'ZConfig==3.0.4',
        'zdaemon==4.0.0',
        'zodb==4.1.0',
    ] + (['zodbpickle==1.0'] if PY2 or PY34 else [])
      + (['Sphinx<1.8.4'] if PY34 or PY2 else [])
      + (['backports.tempfile==1.0'] if PY2 else [])
      + (['Jinja2<2.9'] if PY34 else [])
      + (['scandir'] if PY2 or PY34 else [])
      + (['lxml<4.4.0'] if PY34 else [])
      + (['docutils<0.15'] if PY2 else []),
    version=version,
    packages=['PyOpenWorm',
              'PyOpenWorm.data_trans'],
    author='OpenWorm.org authors and contributors',
    author_email='info@openworm.org',
    description='A Python library for working with OpenWorm data and models',
    long_description=long_description,
    license='MIT',
    url='http://PyOpenWorm.readthedocs.org/en/latest/',
    download_url='https://github.com/openworm/PyOpenWorm/archive/master.zip',
    entry_points={'console_scripts': ['pow = PyOpenWorm.cli:main']},
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
