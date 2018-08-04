Installation
============
The recommended way to get PyOpenWorm is from [pip](http://pip.readthedocs.org/en/latest/installing.html):

    pip install pyopenworm

Alternatively, you can grab the contents from GitHub:

    git clone https://github.com/openworm/PyOpenWorm.git
    cd PyOpenWorm
    python setup.py install

Uninstall
----------

    pip uninstall PyOpenWorm

Running tests
-------------

After checking out the project, tests can be run from the command line in the root folder with::

    py.test

You may also run individual test cases with::

    py.test -k <NameOfTest>

For example, where *test_muscles*1 is a test in the *WormTest* suite of tests (see tests/WormTest.py)::

    py.test -k test_muscles1


Optional
--------
There is an optional database storage option called Sleepycat. You may encounter these issues if you pursue this option:

If your system does not come with bsddb, you will need to install it. On MacOSX, you can follow 
[these instructions](http://stackoverflow.com/questions/16003224/installing-bsddb-package-python) for how to install 
the python library.

If you don't have the Berkeley DB (necessary for using bsddb) you can get it from the [Oracle website](http://www.oracle.com/technetwork/database/database-technologies/berkeleydb/overview/index-085366.html).
