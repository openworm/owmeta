# -*- coding: utf-8 -*-

from setuptools import setup
from setuptools.command.install import install as _install
import os, sys


def _post_install():
    import subprocess
    subprocess.call([sys.executable, 'post_install.py'])

class install(_install):
    def run(self):
        self.do_egg_install()
        self.execute(_post_install, (), msg='Running post-install script(s)')

long_description = open('README.md').read()

setup(
    name = 'PyOpenWorm',
    cmdclass = {'install': install},
    install_requires=[
        'xlrd',
        'libneuroml',
        'zodb==4.1.0',
        'Pint',
        'rdflib>=4.1.2',
        'BTrees==4.0.8',
        'SPARQLWrapper==1.6.2',
        'ZConfig==3.0.4',
        'decorator==3.4.0',
        'discover==0.4.0',
        'html5lib==0.999',
        'isodate==0.5.0',
        'networkx==1.9',
        'numpydoc==0.5',
        'persistent==4.0.8',
        'pyparsing==2.0.2',
        'rdflib_zodb==1.0',
        'requirements==0.1',
        'transaction==1.4.3',
        'wsgiref==0.1.2',
        'zc.lockfile==1.1.0',
        'zdaemon==4.0.0',
        'zope.interface==4.1.1'
    ],
    dependency_links = [
        'git://github.com/NeuralEnsemble/libNeuroML.git#egg=libNeuroML',
        'git://github.com/zopefoundation/ZODB.git#egg=ZODB',
    ],
    setup_requires = "six==1.9.0",
    version = '0.5.0-alpha',
    packages = ['PyOpenWorm'],
    package_data = {'PyOpenWorm':['default.conf']},
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
        'Topic :: Scientific/Engineering'
    ]
)
