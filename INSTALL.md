Installation
============
The recommended way to get owmeta is with [pip](http://pip.readthedocs.org/en/latest/installing.html):

    pip install pyopenworm

Alternatively, you can grab the latest on the development branch from GitHub:

    git clone https://github.com/openworm/owmeta.git
    cd owmeta
    python setup.py install


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

    python setup.py test

You may also run individual test cases with::

    python setup.py test --addopts "-k <NameOfTest>"

For example, where *test_muscles1* is a test in the *WormTest* suite of tests (see tests/WormTest.py)::

    python setup.py test --addopts "-k test_muscles1"

Python 2 support
----------------
Python 2.7 will be supported in owmeta through Python 2.7 end-of-life in
2020. Subsequent to that, any regressions for 2.7-based applications will only
be fixed for the sake of OpenWorm projects when requested by an issue on [our
tracker](https://github.com/openworm/owmeta/issues).


Uninstall
----------

    pip uninstall owmeta


Optional
--------
There is an optional database storage option called Sleepycat. You may encounter these issues if you pursue this option:

If your system does not come with bsddb, you will need to install it. On MacOSX, you can follow 
[these instructions](http://stackoverflow.com/questions/16003224/installing-bsddb-package-python) for how to install 
the python library.

If you don't have the Berkeley DB (necessary for using bsddb) you can get it from the [Oracle website](http://www.oracle.com/technetwork/database/database-technologies/berkeleydb/overview/index-085366.html).
