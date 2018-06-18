.. _coding_standards:

|pow| coding standards
========================================

Pull requests are *required* to follow the PEP-8 Guidelines for contributions of
Python code to PyOpenWorm, with some exceptions noted below. Compliance can be
checked with the ``pep8`` tool and these command line arguments::

    --max-line-length=120 --ignore=E261,E266,E265,E402,E121,E123,E126,E226,E24,E704

Refer to the `pep8 documentation <http://pep8.readthedocs.io/en/release-1.7.x/intro.html#error-codes>`_
for the meanings of these error codes.

Lines of code should only be wrapped before 120 chars for readability. Comments
and string literals, including docstrings, can be wrapped to a shorter length.

Some violations can be corrected with ``autopep8``.
