# -*- coding: utf-8 -*-

from setuptools import setup
import sys

with open('requirements.txt') as f:
    required = f.read().splitlines()

import os

long_description = open("README.md").read()

setup(
    name = "PyOpenWorm",
    install_requires=required,
    dependency_links=[
        "git://github.com/NeuralEnsemble/libNeuroML.git#egg=libNeuroML",
        "git://github.com/zopefoundation/ZODB.git#egg=ZODB",
        ],
    setup_requires="six==1.7.3",
    version = '0.5.0-alpha',
    packages = ['PyOpenWorm'],
    package_data = {"PyOpenWorm":['default.conf']},
    author = "OpenWorm.org authors and contributors",
    author_email = "info@openworm.org",
    description = "A Python library for working with OpenWorm data and models",
    long_description = long_description,
    license = "BSD",
    url="http://PyOpenWorm.readthedocs.org/en/latest/",
    download_url = 'https://github.com/openworm/PyOpenWorm/archive/master.zip',
    classifiers = [
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering']
)
