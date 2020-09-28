.. _test:

Testing in owmeta
=====================

Preparing for tests
-------------------

Within the owmeta project directory, owmeta can be installed for development and testing like this::

    pip install --editable .

The project database should be populated like::

    owm clone https://github.com/openworm/OpenWormData.git

Running tests
-------------
Tests should be run via setup.py like::

    python setup.py test

you can pass options to ``pytest`` like so::

    python setup.py test --addopts '-k DataIntegrityTest'

Writing tests
-------------
Tests are written using Python's unittest. In general, a collection of
closely related tests should be in one file. For selecting different classes of
tests, tests can also be tagged using pytest marks like::

    @pytest.mark.tag
    class TestClass(unittest.TestCase):
        ...

Currently, marks are used to distinguish between unit-level tests and others
which have the ``inttest`` mark. All marks are listed in pytest.ini under
'markers'.
