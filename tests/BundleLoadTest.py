from io import BytesIO
from os import makedirs
from os.path import isdir, join as p
import json
import tarfile

from owmeta.bundle import (Unarchiver,
                           NotABundlePath,
                           TargetDirectoryMismatch,
                           UnarchiveFailed,
                           fmt_bundle_directory)


import pytest


def test_target_directory_possible(tempdir):
    '''
    Test no target_directory or bundles_directory given
    '''
    with pytest.raises(UnarchiveFailed, match='file_name'):
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
    _write_archive(tempdir, {"manifest_version": 1, "version": 12})
    with pytest.raises(NotABundlePath, match=r'file_name.*id'):
        Unarchiver(tempdir).unpack(p(tempdir, 'file_name'))


def test_manifest_lacking_version(tempdir):
    '''
    Test manifest lacking a version raises an exception
    '''
    _write_archive(tempdir, {"manifest_version": 1, "id": "example/aBundle"})
    with pytest.raises(NotABundlePath, match=r'file_name.*version'):
        Unarchiver(tempdir).unpack(p(tempdir, 'file_name'))


def test_target_directory_from_manifest_and_path(tempdir):
    '''
    Test target directory dervied from bundles_directory and bundle manifest
    '''
    _write_archive(tempdir, {"manifest_version": 1, "id": "example/abundle", "version": 12})
    expected_path = p(fmt_bundle_directory(tempdir, 'example/abundle', 12),
                      'manifest')
    Unarchiver(tempdir).unpack(p(tempdir, 'file_name'))
    open(expected_path).close()


def test_target_directory_doesnt_match_derived_target_directory(tempdir):
    '''
    Test target directory dervied from bundles_directory and bundle manifest
    '''
    _write_archive(tempdir, {"manifest_version": 1, "id": "example/abundle", "version": 12})
    expected_target_directory = fmt_bundle_directory(tempdir, 'example/abundle', 12)
    target_directory = fmt_bundle_directory(tempdir, 'example/a-bundle', 12)
    with pytest.raises(TargetDirectoryMismatch, match=r"%s.*%s" % (target_directory,
            expected_target_directory)):
        Unarchiver(tempdir).unpack(p(tempdir, 'file_name'), target_directory)


def test_no_bundles_directory(tempdir):
    '''
    Test target directory given but no bundles_directory -- means no validation
    '''
    _write_archive(tempdir, {"manifest_version": 1, "id": "example/abundle", "version": 12})
    target_directory = fmt_bundle_directory(tempdir, 'example/a-bundle', 12)
    Unarchiver().unpack(p(tempdir, 'file_name'), target_directory)
    assert isdir(target_directory)


def test_bundles_directory_doesnt_exist(tempdir):
    '''
    If the bundles directory doesn't exist, then it is created with no exception
    '''
    _write_archive(tempdir, {
        "manifest_version": 1,
        "id": "example/abundle",
        "version": 12
    })
    Unarchiver(p(tempdir, 'bundles')).unpack(p(tempdir, 'file_name'))
    assert isdir(fmt_bundle_directory(p(tempdir, 'bundles'), 'example/abundle', 12))


def test_target_directory_doesnt_exist(tempdir):
    '''
    If the target directory doesn't exist, then it should be created with no exception
    '''
    _write_archive(tempdir, {
        "manifest_version": 1,
        "id": "example/abundle",
        "version": 12
    })
    Unarchiver().unpack(p(tempdir, 'file_name'), p(tempdir, 'target_directory'))
    assert isdir(p(tempdir, 'target_directory'))


def test_target_directory_not_empty(tempdir):
    '''
    If the target directory is not empty, then an exception should be raised
    '''
    _write_archive(tempdir, {
        "manifest_version": 1,
        "id": "example/abundle",
        "version": 12
    })

    expected_target_directory = fmt_bundle_directory(tempdir, 'example/abundle', 12)
    makedirs(expected_target_directory)
    open(p(expected_target_directory, 'bluh'), 'w').close()

    with pytest.raises(UnarchiveFailed):
        Unarchiver(tempdir).unpack(p(tempdir, 'file_name'))


def test_archive_path_within_target(tempdir):
    '''
    If the archive contains a path that points outside of the target directory, then an
    exception should be raised
    '''
    _write_archive(tempdir, {
        "manifest_version": 1,
        "id": "example/abundle",
        "version": 12
    }, ('../invalid_file', b''))

    with pytest.raises(NotABundlePath):
        Unarchiver(tempdir).unpack(p(tempdir, 'file_name'))


def test_clear_target_directory_on_invalid_file_path(tempdir):
    '''
    If the archive contains a path that points outside of the target directory, then an
    exception should be raised
    '''
    _write_archive(tempdir, {
        "manifest_version": 1,
        "id": "example/abundle",
        "version": 12
    }, ('../invalid_file', b''))

    try:
        Unarchiver(tempdir).unpack(p(tempdir, 'file_name'))
    except Exception:
        pass
    assert not isdir(fmt_bundle_directory(tempdir, 'example/abundle', 12))


def _write_archive(tempdir, manifest_contents, *files):
    manifest_contents = json.dumps(manifest_contents).encode('UTF-8')
    with tarfile.open(p(tempdir, 'file_name'), 'w:xz') as f:
        tinfo = tarfile.TarInfo('./manifest')
        tinfo.size = len(manifest_contents)
        f.addfile(tinfo, fileobj=BytesIO(manifest_contents))
        for additional_file in files:
            tinfo = tarfile.TarInfo(additional_file[0])
            tinfo.size = len(additional_file[1])
            f.addfile(tinfo, fileobj=BytesIO(additional_file[1]))
