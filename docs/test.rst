.. _test:

Testing in PyOpenWorm
=====================

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
which have the ``inttest`` mark

