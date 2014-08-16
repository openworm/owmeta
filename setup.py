# -*- coding: utf-8 -*-

from setuptools import setup
import sys

with open('requirements.txt') as f:
    required = f.read().splitlines()

import os
# Build the database if we're doing an install
if (len(sys.argv) > 1) \
    and (sys.argv[1] in ('install','build')) \
    and not os.path.isdir('./db/worm.db'):
    from db import insert_worm
    # From: http://stackoverflow.com/questions/431684/how-do-i-cd-in-python
    #------------
    class cd:
        """Context manager for changing the current working directory"""
        def __init__(self, newPath):
            self.newPath = newPath

        def __enter__(self):
            self.savedPath = os.getcwd()
            os.chdir(self.newPath)

        def __exit__(self, etype, value, traceback):
            os.chdir(self.savedPath)
    #-----------

    with cd('./db'):
        print 'Compiling C. elegans data'
        insert_worm.do_insert()

    if not os.path.isdir('./db/worm.db'):
        sys.exit(-1)

long_description = open("README.md").read()

setup(
    name = "PyOpenWorm",
    version = '0.5.0-alpha',
    packages = ['PyOpenWorm', 'tests', 'db'],
    package_data = dict(
        db=['default.conf', 'worm.db/*']
        ),
    author = "OpenWorm.org authors and contributors",
    author_email = "info@openworm.org",
    description = "A Python library for working with OpenWorm data and models",
    long_description = long_description,
    license = "BSD",
    url="http://github.com/openworm/pyopenworm",
    download_url = 'https://github.com/openworm/PyOpenWorm/tarball/0.0.1-alpha',
    classifiers = [
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering']
)
