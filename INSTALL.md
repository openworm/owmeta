Installation
============
The recommended way to get PyOpenWorm is from [pip](http://pip.readthedocs.org/en/latest/installing.html):

    pip install pyopenworm

Alternatively, you can grab the latest on the development branch from GitHub:

    git clone https://github.com/openworm/PyOpenWorm.git
    cd PyOpenWorm
    python setup.py install

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
Python 2.7 will be supported in PyOpenWorm through Python 2.7 end-of-life in 2020. Subsequent to that, any regressions for 2.7-based applications will only be fixed for the sake of OpenWorm projects.


Uninstall
----------

    pip uninstall PyOpenWorm


Optional
--------
There is an optional database storage option called Sleepycat. You may encounter these issues if you pursue this option:

If your system does not come with bsddb, you will need to install it. On MacOSX, you can follow 
[these instructions](http://stackoverflow.com/questions/16003224/installing-bsddb-package-python) for how to install 
the python library.

If you don't have the Berkeley DB (necessary for using bsddb) you can get it from the [Oracle website](http://www.oracle.com/technetwork/database/database-technologies/berkeleydb/overview/index-085366.html).
