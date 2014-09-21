# -*- coding: utf-8 -*-

from setuptools import setup
import sys

with open('requirements.txt') as f:
    required = f.read().splitlines()

import os

long_description = open("README.md").read()

setup(
    name = "OpenWormData",
    install_requires=required,
    dependency_links=[
        "git://github.com/zopefoundation/ZODB.git#egg=ZODB",
        ],
    version = '0.0.1-alpha',
    packages = ['OpenWormData'],
    package_data = {"OpenWormData":['default.conf']},
    author = "OpenWorm.org authors and contributors",
    author_email = "info@openworm.org",
    description = "A database of information about the c. elegans",
    long_description = long_description,
    license = "MIT",
    url="http://PyOpenWorm.readthedocs.org/en/latest/",
    download_url = 'https://github.com/openworm/OpenWormData/archive/master.zip',
    classifiers = [
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering']
)
