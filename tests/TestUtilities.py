from __future__ import absolute_import
from __future__ import print_function
import os
import hashlib
from contextlib import contextmanager
from six import StringIO, string_types
import logging
import re

import pytest


excludedFiles = ['TestUtilities.py', 'pytest_profile.py']


def findSkippedTests():
    skippedTest = '@unittest.skip'
    expectedFailure = '@unittest.expectedFailure'

    # The boolean count is to make sure that multiple new lines aren't printed
    # in the event that multiple files have neither skipped tests nor
    # expected failures.

    for fname in os.listdir('.'):
        if os.path.isfile(fname) and fname[-3:] == ".py" and fname not in excludedFiles:
            with open(fname) as f:
                count = False
                for line in f:
                    if skippedTest in line:
                        print('found skipped test in file %s' % fname)
                        count = True
                    elif expectedFailure in line:
                        print('found expected failure in file %s' % fname)
                        count = True
                if count:
                    print('\n')
                    count = False


# Function to list function names in test suite so we can quickly see \
# which ones do not adhere to the proper naming convention.
def listFunctionNames():
    for fname in os.listdir('.'):
        if os.path.isfile(fname) and fname[-3:] == ".py" and fname not in excludedFiles:
            with open(fname) as f:
                count = False
                for line in f:
                    check = line.strip()[4:8]
                    if 'def ' in line and check != 'test' and check != '__in':
                        print(line.strip() + ' in file ' + fname)
                        count = True

                if count:
                    print('\n')
                    count = False


def xfail_without_db():
    db_path = os.path.join(
        os.path.dirname(  # project root
            os.path.dirname(  # test dir
                os.path.realpath(__file__)  # this file
            )
        ),
        ".owm",
        "worm.db"
    )

    if not os.path.isfile(db_path):
        pytest.xfail("Database is not installed. Try \n\towm clone https://github.com/openworm/OpenWormData.git")


# Add function to find dummy tests, i.e. ones that are simply marked pass.
# TODO: improve this to list function names
def findDummyTests():
    for fname in os.listdir('.'):
        if os.path.isfile(fname) and fname[-3:] == ".py" and fname not in excludedFiles:
            with open(fname) as f:
                count = False
                for line in f:
                    if 'pass' in line:
                        print('dummy test in file ' + fname)
                        count = True

                if count:
                    print('\n')
                    count = False


@contextmanager
def noexit():
    try:
        yield
    except SystemExit:
        pass


@contextmanager
def stdout():
    import sys
    oldstdout = sys.stdout
    sio = StringIO()
    sys.stdout = sio
    try:
        yield sys.stdout
    finally:
        sys.stdout = oldstdout


@contextmanager
def stderr():
    import sys
    oldstderr = sys.stderr
    sio = StringIO()
    sys.stderr = sio
    try:
        yield sys.stderr
    finally:
        sys.stderr = oldstderr


@contextmanager
def captured_logging():
    out = StringIO()
    logger = logging.getLogger()
    stream_handler = logging.StreamHandler(out)
    logger.addHandler(stream_handler)
    try:
        yield out
    finally:
        logger.removeHandler(stream_handler)
        out.close()


def assertRegexpMatches(text, pattern):
    if isinstance(pattern, string_types):
        pattern = re.compile(pattern)
    if not pattern.search(text):
        raise AssertionError('Could not find {} in:\n{}'.format(pattern, text))


def assertNotRegexpMatches(text, pattern):
    if isinstance(pattern, string_types):
        pattern = re.compile(pattern)
    if pattern.search(text):
        raise AssertionError('Unexpectedly found {} in:\n{}'.format(pattern, text))
