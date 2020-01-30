import pytest
from unittest.mock import patch, Mock
import re

from owmeta.bundle import HTTPBundleLoader, URLConfig, LoadFailed


def test_can_load_from_http():
    assert HTTPBundleLoader.can_load_from(URLConfig('http://'))


def test_can_load_from_https():
    assert HTTPBundleLoader.can_load_from(URLConfig('https://'))


def test_cannot_load_from_ftp():
    assert not HTTPBundleLoader.can_load_from(URLConfig('ftp://'))


def test_cannot_load_from_None():
    assert not HTTPBundleLoader.can_load_from(None)


def test_cannot_load_in_index_with_no_releases_no_version_provided():
    cut = HTTPBundleLoader('index_url')
    with patch('requests.get') as get:
        get().json.return_value = {'test_bundle': {}}
        assert not cut.can_load('test_bundle')


def test_cannot_load_in_index_with_releases_but_no_url_and_no_version_provided():
    cut = HTTPBundleLoader('index_url')
    with patch('requests.get') as get:
        get().json.return_value = {'test_bundle': {'1': ''}}
        assert not cut.can_load('test_bundle')


def test_cannot_load_in_index_with_releases_but_bad_url_no_version_provided():
    cut = HTTPBundleLoader('index_url')
    with patch('requests.get') as get:
        get().json.return_value = {'test_bundle': {'1': 'http://'}}
        assert not cut.can_load('test_bundle')


def test_can_load_in_index_with_releases_no_version_provided():
    cut = HTTPBundleLoader('index_url')
    with patch('requests.get') as get:
        get().json.return_value = {'test_bundle': {'1': 'http://some_host'}}
        assert cut.can_load('test_bundle')


def test_cannot_load_in_index_with_releases_but_no_matching_version_provided():
    cut = HTTPBundleLoader('index_url')
    with patch('requests.get') as get:
        get().json.return_value = {'test_bundle': {'1': 'http://some_host'}}
        assert not cut.can_load('test_bundle', 2)


def test_cannot_load_in_index_with_no_releases():
    cut = HTTPBundleLoader('index_url')
    with patch('requests.get') as get:
        get().json.return_value = {'test_bundle': {}}
        assert not cut.can_load('test_bundle', 2)


def test_cannot_load_not_in_index():
    cut = HTTPBundleLoader('index_url')
    with patch('requests.get') as get:
        get().json.return_value = {}
        assert not cut.can_load('test_bundle', 2)


def test_can_load_in_index_with_releases_and_matching_version_provided():
    cut = HTTPBundleLoader('index_url')
    with patch('requests.get') as get:
        get().json.return_value = {'test_bundle': {'1': 'http://some_host'}}
        assert cut.can_load('test_bundle', 1)


def test_bundle_versions_multiple():
    cut = HTTPBundleLoader('index_url')
    with patch('requests.get') as get:
        get().json.return_value = {'test_bundle': {
            '1': 'http://some_host',
            '2': 'http://some_host'
        }}
        assert set(cut.bundle_versions('test_bundle')) == set([1, 2])


def test_bundle_versions_skips_non_int():
    cut = HTTPBundleLoader('index_url')
    with patch('requests.get') as get:
        get().json.return_value = {'test_bundle': {
            '1': 'http://some_host',
            'oops': 'http://some_host',
            '2': 'http://some_host'
        }}
        assert set(cut.bundle_versions('test_bundle')) == set([1, 2])


def test_load_fail_no_info():
    cut = HTTPBundleLoader('index_url')
    with patch('requests.get') as get:
        get().json.return_value = {}
        with pytest.raises(LoadFailed, match='not in.*index'):
            cut.load('test_bundle')


def test_load_fail_wrong_type_of_info():
    cut = HTTPBundleLoader('index_url')
    with patch('requests.get') as get:
        get().json.return_value = {'test_bundle': ["wut"]}
        with pytest.raises(LoadFailed, match='type.*bundle info'):
            cut.load('test_bundle')


def test_load_fail_no_valid_release_number():
    cut = HTTPBundleLoader('index_url')
    with patch('requests.get') as get:
        get().json.return_value = {'test_bundle': {'smack': 'down'}}
        with pytest.raises(LoadFailed,
                match=re.compile('no releases found', re.I)):
            cut.load('test_bundle')


def test_load_fail_no_valid_bundle_url():
    cut = HTTPBundleLoader('index_url')
    with patch('requests.get') as get:
        get().json.return_value = {'test_bundle': {'1': 'down'}}
        with pytest.raises(LoadFailed,
                match=re.compile('valid url', re.I)):
            cut.load('test_bundle')


def test_load_fail_no_valid_bundle_url():
    cut = HTTPBundleLoader('index_url')
    with patch('requests.get') as get:
        get().json.return_value = {'test_bundle': {'1': 'down'}}
        with pytest.raises(LoadFailed,
                match=re.compile('valid url', re.I)):
            cut.load('test_bundle')


def test_load_no_cachedir():
    from io import BytesIO
    cut = HTTPBundleLoader('index_url')
    cut.base_directory = 'bdir'
    with patch('requests.get') as get, patch('owmeta.bundle.Unarchiver') as Unarchiver:
        raw_response = Mock(name='raw_response')
        get().json.return_value = {'test_bundle': {'1': 'http://some_host'}}
        get().raw.read.return_value = b'bytes bytes bytes'
        cut.load('test_bundle')
        Unarchiver().unpack.assert_called_with(MatchingBytesIO(BytesIO(b'bytes bytes bytes')), 'bdir')


class MatchingBytesIO(object):
    def __init__(self, bio):
        self.bio = bio

    def __eq__(self, other):
        return self.bio.getvalue() == other.getvalue()
