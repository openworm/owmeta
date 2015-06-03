# -*- coding: utf-8 -*-

from setuptools import setup
from setuptools.command.install import install as _install
import os, sys

def _post_install():
    from subprocess import call
    import shutil, glob
    pwd = os.path.dirname(os.path.realpath(__file__))
    script_location = os.path.join(pwd, 'OpenWormData', 'scripts')
    call([sys.executable, 'insert_worm.py'],
         cwd = script_location)
    # move created database files to top directory
    db_files = glob.glob(os.path.join(script_location, 'worm.db*'))
    for db_file in db_files:
        shutil.move(db_file, pwd)

class install(_install):
    def run(self):
        _install.run(self)
        self.execute(_post_install, (), msg='Running post-install script(s)')

with open('requirements.txt') as f:
    required = f.read().splitlines()

long_description = open('README.md').read()

setup(
    name = 'PyOpenWorm',
    cmdclass = {'install': install},
    install_requires = required,
    dependency_links = [
        'git://github.com/NeuralEnsemble/libNeuroML.git#egg=libNeuroML',
        'git://github.com/zopefoundation/ZODB.git#egg=ZODB',
    ],
    setup_requires = "six==1.7.3",
    version = '0.5.0-alpha',
    packages = ['PyOpenWorm'],
    package_data = {'PyOpenWorm':['default.conf']},
    author = 'OpenWorm.org authors and contributors',
    author_email = 'info@openworm.org',
    description = 'A Python library for working with OpenWorm data and models',
    long_description = long_description,
    license = 'BSD',
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
