from unittest.mock import patch
from owmeta.bundle import HTTPBundleLoader, URLConfig


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
