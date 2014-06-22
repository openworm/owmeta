# -*- coding: utf-8 -*-

from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

long_description = open("README.md").read()

setup(
    install_requires=required,
    name = "PyOpenWorm",
    version = '0.0.1-alpha',
    packages = ['PyOpenWorm', 'tests'],
    author = "OpenWorm.org authors and contributors",
    author_email = "info@openworm.org",
    description = "A Python library for working with OpenWorm data and models",
    long_description = long_description,
    license = "BSD",
    url="http://github.com/openworm/pyopenworms",
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