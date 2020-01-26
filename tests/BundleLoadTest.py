from io import BytesIO
import tempfile
from os.path import join as p
from os import makedirs, chmod
import tarfile

from owmeta.bundle import Unarchiver, NotABundlePath, fmt_bundle_directory


import pytest


def test_target_directory_possible(tempdir):
    '''
    Test no target_directory or bundles_directory given
    '''
    with pytest.raises(Exception, match='file_name'):
        Unarchiver().unpack(p(tempdir, 'file_name'))


def test_input_file_not_found(tempdir):
    '''
    Test the exception thrown when the input file is not found on disk
    '''
    with pytest.raises(NotABundlePath, match='file_name.*not found'):
        Unarchiver(tempdir).unpack(p(tempdir, 'file_name'))


def test_input_file_format_is_unexpected(tempdir):
    '''
    Test the exception when the input file is not in a format we support
    '''
    open(p(tempdir, 'file_name'), 'w').close()
    with pytest.raises(NotABundlePath, match='file_name.*read.*archive'):
        Unarchiver(tempdir).unpack(p(tempdir, 'file_name'))


def test_manifest_missing_from_archive(tempdir):
    '''
    Test manifest missing from archive file raises exception
    '''
    tarfile.open(p(tempdir, 'file_name'), 'w:xz').close()
    with pytest.raises(NotABundlePath, match='file_name.*manifest'):
        Unarchiver(tempdir).unpack(p(tempdir, 'file_name'))


def test_manifest_lacking_id(tempdir):
    '''
    Test manifest lacking an id raises an exception
    '''
    _write_archive(tempdir, b'{"version": 12}')
    with pytest.raises(NotABundlePath, match=r'file_name.*id'):
        Unarchiver(tempdir).unpack(p(tempdir, 'file_name'))


def test_manifest_lacking_version(tempdir):
    '''
    Test manifest lacking a version raises an exception
    '''


def test_target_directory_from_manifest_and_path(tempdir):
    '''
    Test target directory dervied from bundles_directory and bundle manifest
    '''
    _write_archive(tempdir, b'{"id": "example/abundle", "version": 12}')
    expected_path = p(fmt_bundle_directory(tempdir, 'example/abundle', 12),
                      'manifest')
    Unarchiver(tempdir).unpack(p(tempdir, 'file_name'))
    open(expected_path).close()


def test_target_directory_doesnt_match_derived_target_directory(tempdir):
    '''
    Test target directory dervied from bundles_directory and bundle manifest
    '''


def test_no_bundles_directory(tempdir):
    '''
    Test target directory given but no bundles_directory -- means no validation
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


def _write_archive(tempdir, manifest_contents):
    with tarfile.open(p(tempdir, 'file_name'), 'w:xz') as f:
        tinfo = tarfile.TarInfo('manifest')
        tinfo.size = len(manifest_contents)
        f.addfile(tinfo, fileobj=BytesIO(manifest_contents))
