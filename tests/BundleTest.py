from io import StringIO
import tempfile
from os.path import join as p
from os import makedirs, chmod

from owmeta.bundle import (Remote, URLConfig, HTTPBundleLoader, Bundle, BundleNotFound,
                           Descriptor, DependencyDescriptor)


import pytest


def test_write_read_remote_1():
    out = StringIO()
    r0 = Remote('remote')
    r0.write(out)
    out.seek(0)
    r1 = Remote.read(out)
    assert r0 == r1


def test_write_read_remote_2():
    out = StringIO()
    r0 = Remote('remote')
    r0.accessor_configs.append(URLConfig('http://example.org/bundle_remote0'))
    r0.accessor_configs.append(URLConfig('http://example.org/bundle_remote1'))
    r0.write(out)
    out.seek(0)
    r1 = Remote.read(out)
    assert r0 == r1


def test_get_http_url_loaders():
    '''
    Find loaders for HTTP URLs
    '''
    out = StringIO()
    r0 = Remote('remote')
    r0.accessor_configs.append(URLConfig('http://example.org/bundle_remote0'))
    for l in r0.generate_loaders():
        if isinstance(l, HTTPBundleLoader):
            return

    raise AssertionError('No HTTPBundleLoader was created')


def test_latest_bundle_fetched():
    with tempfile.TemporaryDirectory(prefix=__name__ + '.') as tempdir:
        bundles_directory = p(tempdir, 'bundles')
        makedirs(p(bundles_directory, 'example', '1'))
        makedirs(p(bundles_directory, 'example', '2'))
        expected = p(bundles_directory, 'example', '3')
        makedirs(expected)
        b = Bundle('example', bundles_directory=bundles_directory)
        assert expected == b._get_bundle_directory()


def test_specified_version_fetched():
    with tempfile.TemporaryDirectory(prefix=__name__ + '.') as tempdir:
        bundles_directory = p(tempdir, 'bundles')
        makedirs(p(bundles_directory, 'example', '1'))
        expected = p(bundles_directory, 'example', '2')
        makedirs(expected)
        makedirs(p(bundles_directory, 'example', '3'))
        b = Bundle('example', version=2, bundles_directory=bundles_directory)
        assert expected == b._get_bundle_directory()


def test_no_versioned_bundles():
    with tempfile.TemporaryDirectory(prefix=__name__ + '.') as tempdir:
        bundles_directory = p(tempdir, 'bundles')
        makedirs(p(bundles_directory, 'example'))
        b = Bundle('example', bundles_directory=bundles_directory)
        with pytest.raises(BundleNotFound, match='No versioned bundle directories'):
            b._get_bundle_directory()


def test_specified_bundle_does_not_exist():
    with tempfile.TemporaryDirectory(prefix=__name__ + '.') as tempdir:
        bundles_directory = p(tempdir, 'bundles')
        makedirs(p(bundles_directory, 'example'))
        b = Bundle('example', bundles_directory=bundles_directory, version=2)
        with pytest.raises(BundleNotFound, match='at version 2.*specified version'):
            b._get_bundle_directory()


def test_specified_bundle_directory_does_not_exist():
    with tempfile.TemporaryDirectory(prefix=__name__ + '.') as tempdir:
        bundles_directory = p(tempdir, 'bundles')
        makedirs(bundles_directory)
        b = Bundle('example', bundles_directory=bundles_directory)
        with pytest.raises(BundleNotFound, match='Bundle directory'):
            b._get_bundle_directory()


def test_specified_bundles_root_directory_does_not_exist():
    with tempfile.TemporaryDirectory(prefix=__name__ + '.') as tempdir:
        bundles_directory = p(tempdir, 'bundles')
        b = Bundle('example', bundles_directory=bundles_directory)
        with pytest.raises(BundleNotFound, match='Bundle directory'):
            b._get_bundle_directory()


def test_specified_bundles_root_permission_denied():
    with tempfile.TemporaryDirectory(prefix=__name__ + '.') as tempdir:
        bundles_directory = p(tempdir, 'bundles')
        b = Bundle('example', bundles_directory=bundles_directory)
        makedirs(bundles_directory)
        chmod(bundles_directory, 0)
        try:
            with pytest.raises(OSError, match='[Pp]ermission denied'):
                b._get_bundle_directory()
        finally:
            chmod(bundles_directory, 0o777)


def test_ignore_non_version_number():
    with tempfile.TemporaryDirectory(prefix=__name__ + '.') as tempdir:
        bundles_directory = p(tempdir, 'bundles')
        b = Bundle('example', bundles_directory=bundles_directory)
        makedirs(p(bundles_directory, 'example', 'ignore_me'))
        expected = p(bundles_directory, 'example', '5')
        makedirs(expected)
        actual = b._get_bundle_directory()
        assert actual == expected


def test_descriptor_dependency():
    d = Descriptor.make({
        'id': 'testBundle',
        'dependencies': [
            'dep1',
            {'id': 'dep2', 'version': 2},
            ('dep3', 4),
            ('dep4',)
        ]
    })
    assert DependencyDescriptor('dep1') in d.dependencies
    assert DependencyDescriptor('dep2', 2) in d.dependencies
    assert DependencyDescriptor('dep3', 4) in d.dependencies
    assert DependencyDescriptor('dep4') in d.dependencies
