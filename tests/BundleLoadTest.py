from io import StringIO
import tempfile
from os.path import join as p
from os import makedirs, chmod

from owmeta.bundle import Unarchiver


import pytest


def test_target_directory_possible(tempdir):
    '''
    Test no target_directory or bundles_directory given
    '''


def test_target_directory_from_manifest_and_path(tempdir):
    '''
    Test target directory dervied from bundles_directory and bundle manifest
    '''


def test_target_directory_doesnt_match_derived_target_directory(tempdir):
    '''
    Test target directory dervied from bundles_directory and bundle manifest
    '''


def test_no_bundles_directory(tempdir):
    '''
    Test target directory given but no bundles_directory -- means no validation
    '''


def test_manifest_missing_from_archive(tempdir):
    '''
    Test manifest missing from archive file raises exception
    '''


def test_manifest_lacking_id(tempdir):
    '''
    Test manifest lacking an id raises an exception
    '''


def test_manifest_lacking_version(tempdir):
    '''
    Test manifest lacking a version raises an exception
    '''


def test_bundles_directory_doesnt_exist(tempdir):
    '''
    If the bundles directory doesn't exist, then it should be created and no exception
    raised
    '''


def test_target_directory_doesnt_exist(tempdir):
    '''
    If the target directory doesn't exist, then it should be created with no exception
    '''


def test_target_directory_not_empty(tempdir):
    '''
    If the target directory is not empty, then an exception should be raised
    '''
