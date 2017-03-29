# -*- coding: utf-8 -*-
#

from setuptools import setup
from setuptools.command.install import install as _install
import sys


def _post_install():
    import subprocess
    subprocess.call([sys.executable, 'post_install.py'])

class install(_install):
    def run(self):
        self.do_egg_install()
        self.execute(_post_install, (), msg='Running post-install script(s)')

long_description = """
PyOpenWorm
===========

A unified, simple data access library in Python for data, facts, and models of
*C. elegans* anatomy for the [OpenWorm project](http://www.openworm.org)

What does it do?
----------------

Enables a simple Python API for asking various questions about the cells of the
*C. elegans*, enabling the sharing of data about *C. elegans* for the purpose
of building a [data-to-model pipeline](http://docs.openworm.org/en/latest/projects
for the OpenWorm project. In addition, it is a repository for various iterations
of inferred / predicted data about *C. elegans*. Uncontroversial facts and
inferred information are distinguished through the use of explicit Evidence
references.
"""


for line in open('PyOpenWorm/__init__.py'):
    if line.startswith("__version__"):
        version = line.split("=")[1].strip()[1:-1]
setup(
    name = 'PyOpenWorm',
    cmdclass = {'install': install},
    zip_safe = False,
    install_requires=[
        'bibtexparser==0.6.1',
        'BTrees==4.0.8',
        'decorator==3.4.0',
        'discover==0.4.0',
        'html5lib==0.999',
        'isodate==0.5.0',
        'libneuroml',
        'networkx==1.9',
        'numpydoc==0.5',
        'persistent==4.0.8',
        'Pint',
        'pyparsing==2.0.2',
        'pytest>=3.0.6',
        'pytest-cov==2.0.0',
        'rdflib==4.1.2',
        'rdflib-zodb>=1.0.0',
        'requirements==0.1',
        'requests',
        'six==1.9.0',
        'SPARQLWrapper==1.6.2',
        'transaction==1.4.4',
        'xlrd',
        'yarom==0.9.0',
        'zc.lockfile==1.1.0',
        'ZConfig==3.0.4',
        'zdaemon==4.0.0',
        'zodb==4.1.0',
        'zope.interface==4.1.1',
        'FuXi',
        'lazy-object-proxy==1.2.1',
        'wrapt'
    ],
    dependency_links = [
        'git://github.com/NeuralEnsemble/libNeuroML.git#egg=libNeuroML',
        'git://github.com/zopefoundation/ZODB.git#egg=ZODB',
        'git://github.com/RDFLib/FuXi#egg=FuXi-1.4.dev-r0',
        'git://github.com/mwatts15/rdflib-zodb.git@pow-90#egg=rdflib-zodb-1.1-dev'
    ],
    version = version,
    packages = ['PyOpenWorm'],
    package_data = {
        'PyOpenWorm': ['default.conf']
    },
    include_package_data=True,
    author = 'OpenWorm.org authors and contributors',
    author_email = 'info@openworm.org',
    description = 'A Python library for working with OpenWorm data and models',
    long_description = long_description,
    license = 'MIT',
    url='http://PyOpenWorm.readthedocs.org/en/latest/',
    download_url = 'https://github.com/openworm/PyOpenWorm/archive/master.zip',
    classifiers = [
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Topic :: Scientific/Engineering'
    ]
)
