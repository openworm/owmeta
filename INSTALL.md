Installation
------------
Typically the steps below should be sufficient for a successful install

    git clone https://github.com/openworm/PyOpenWorm.git
    cd PyOpenWorm
    pip install -r requirements.txt
    python setup.py install

However, some users have experienced difficulty installing on Mac OSX. If the install
fails when attempting to instal lxml, you might try installing it separately before
attempting to install PyOpenWorm. At least one user has found this [Stack Overflow](http://stackoverflow.com/questions/19548011/cannot-install-lxml-on-mac-os-x-10-9)
post to be helpful.

You may also experience difficulty with a mismatch between your bsddb version and the one used to create the database.

If your system does not come with bsddb, you will need to install it.  On MacOSX, follow [these instructions](http://stackoverflow.com/questions/16003224/installing-bsddb-package-python)

    
Uninstall
----------

    pip uninstall PyOpenWorm

Running tests
-------------

After checking out the project, tests can be run on the command line with::

    python -m unittest discover -s tests