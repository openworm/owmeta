Installation
============
The recommended way to get PyOpenWorm is from [pip](http://pip.readthedocs.org/en/latest/installing.html):

    pip install pyopenworm

However, some users have experienced difficulty installing on Mac OSX. If the install
fails when attempting to install lxml, you might try installing it separately before
attempting to install PyOpenWorm. At least one user has found this [Stack Overflow](http://stackoverflow.com/questions/19548011/cannot-install-lxml-on-mac-os-x-10-9)
post to be helpful.

Alternatively, you can grab the contents from GitHub:

    git clone https://github.com/openworm/PyOpenWorm.git
    cd PyOpenWorm
    python setup.py install

Uninstall
----------

    pip uninstall PyOpenWorm

Running tests
-------------

After checking out the project, tests can be run on the command line with::

    python tests/test.py


Optional
--------
There is an optional database storeage option called Sleepycat. You may encounter these issues if you pursue this option:

If your system does not come with bsddb, you will need to install it. On MacOSX, you can follow 
[these instructions](http://stackoverflow.com/questions/16003224/installing-bsddb-package-python) for how to install 
the python library.

If you don't have the Berkeley DB (necessary for using bsddb) you can get it from the [Oracle website](http://www.oracle.com/technetwork/database/database-technologies/berkeleydb/overview/index-085366.html).
