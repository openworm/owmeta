# -*- coding: utf-8 -*-

from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

long_description = open("README.md").read()

setup(
    #data_files=[("",['neuroml/test/Purk2M9s.nml'])],
    install_requires=required,
    name = "PyOpenWorm",
    version = '0.5',
    packages = ['PyOpenWorm', 'tests'],
    #package_data = {'neuroml.test': ['*.nml']},
    author = "OpenWorm.org authors and contributors",
    author_email = "info@openworm.org",
    description = "A Python library for working with OpenWorm data and models",
    long_description = long_description,
    license = "BSD",
    url="http://PyOpenWorm.readthedocs.org/en/latest/",
    classifiers = [
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering']
)