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
        get().json.return_value = {'test_bundle': {1: ''}}
        assert not cut.can_load('test_bundle')


def test_cannot_load_in_index_with_releases_but_bad_url_no_version_provided():
    cut = HTTPBundleLoader('index_url')
    with patch('requests.get') as get:
        get().json.return_value = {'test_bundle': {1: 'http://'}}
        assert not cut.can_load('test_bundle')


def test_can_load_in_index_with_releases_no_version_provided():
    cut = HTTPBundleLoader('index_url')
    with patch('requests.get') as get:
        get().json.return_value = {'test_bundle': {1: 'http://some_host'}}
        assert cut.can_load('test_bundle')
