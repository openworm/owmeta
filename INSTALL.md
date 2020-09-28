Installation
============
The recommended way to get owmeta is with [pip](http://pip.readthedocs.org/en/latest/installing.html):

    pip install owmeta

Alternatively, you can grab the latest on the development branch from GitHub:

    git clone https://github.com/openworm/owmeta.git
    cd owmeta
    pip install -e .

OWM Database
------------
`owm` is a command line installed with owmeta which provides a high-level
interface for interacting with data created with owmeta. Although you can
use owmeta without it, there is an OpenWorm database which is managed with
`owm`. You can clone this database by running the following command:

    owm clone https://github.com/openworm/OpenWormData.git

This will create a directory `.owm` in your current working directory,
underneath which, the database and related files are stored. See documentation
for the command on ReadTheDocs.io
[here](https://pyopenworm.readthedocs.io/en/dev/command.html) or look at
docs/command.rst. 

Running tests
-------------

After checking out the project, tests can be run from the command line in the root folder with::

    pytest

You may also run individual test cases with::

    pytest -k <NameOfTest>

For example, to run ``test_muscles1`` in the ``WormTest`` suite of tests (see tests/WormTest.py)::

    pytest -k test_muscles1

Uninstall
----------

To uninstall owmeta::

    pip uninstall owmeta
