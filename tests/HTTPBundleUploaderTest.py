from os.path import join as p
import logging

from owmeta.bundle import HTTPBundleUploader, HTTPSURLConfig, BUNDLE_ARCHIVE_MIME_TYPE


L = logging.getLogger(__name__)


def test_bundle_upload_directory(http_server, tempdir):
    '''
    Uploading a directory requires that we turn it into an archive first.
    '''
    cut = HTTPBundleUploader(http_server.url)
    with open(p(tempdir, 'random_file'), 'w') as f:
        f.write("smashing")

    cut(tempdir)

    req = http_server.requests.get()
    while req['method'] != 'POST':
        req = http_server.requests.get()

    assert req['headers']['content-type'] == BUNDLE_ARCHIVE_MIME_TYPE


def test_bundle_upload_directory_to_https(https_server, tempdir):
    cut = HTTPBundleUploader(https_server.url, ssl_context=https_server.ssl_context)
    with open(p(tempdir, 'random_file'), 'w') as f:
        f.write("smashing")

    cut(tempdir)

    req = https_server.requests.get()
    while req['method'] != 'POST':
        req = https_server.requests.get()

    assert req['headers']['content-type'] == BUNDLE_ARCHIVE_MIME_TYPE


def test_bundle_upload_directory_to_https_by_urlconfig(https_server, tempdir):
    cut = HTTPBundleUploader(HTTPSURLConfig(
        https_server.url, ssl_context=https_server.ssl_context))
    with open(p(tempdir, 'random_file'), 'w') as f:
        f.write("smashing")

    cut(tempdir)

    req = https_server.requests.get()
    while req['method'] != 'POST':
        req = https_server.requests.get()

    assert req['headers']['content-type'] == BUNDLE_ARCHIVE_MIME_TYPE


def test_bundle_upload_archive(http_server):
    pass
