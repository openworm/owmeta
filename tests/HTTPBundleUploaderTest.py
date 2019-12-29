import tempfile
import shutil
from os import chdir
from os.path import join as p
from multiprocessing import Process, Queue
from http.server import HTTPServer, SimpleHTTPRequestHandler

from pytest import fixture, raises
import requests

from owmeta.bundle import HTTPBundleUploader, BUNDLE_ARCHIVE_MIME_TYPE


class ServerData():
    def __init__(self, server, request_queue):
        self.server = server
        self.requests = request_queue
        self.url = 'http://{}:{}'.format(*server.server_address)


@fixture
def http_server():
    srvdir = tempfile.mkdtemp(prefix=__name__ + '.')
    process = None
    request_queue = Queue()
    try:
        server = make_server(request_queue)

        def pfunc():
            chdir(srvdir)
            server.serve_forever()

        process = Process(target=pfunc)
        process.start()
        wait_for_started(server.server_address)
        yield ServerData(server, request_queue)
    finally:
        if process:
            process.terminate()
            process.join()
        shutil.rmtree(srvdir)


@fixture
def testdir():
    testdir = tempfile.mkdtemp(prefix=__name__ + '.')
    try:
        yield testdir
    finally:
        shutil.rmtree(testdir)


def make_server(request_queue):
    class _Handler(SimpleHTTPRequestHandler):
        def do_POST(self):
            request_queue.put(dict(
                method=self.command,
                path=self.path,
                headers={k.lower(): v for k, v in self.headers.items()}))
            self.send_response(201)
            self.end_headers()

    port = 8000
    while True:
        try:
            server = HTTPServer(('127.0.0.1', port), _Handler)
            break
        except OSError as e:
            if e.errno != 98:
                raise
            port += 1

    return server


def wait_for_started(server_addr):
    done = False
    while not done:
        try:
            requests.head('http://{}:{}'.format(*server_addr))
            done = True
        except Exception:
            L.info("Unable to connect to the bundle server. Trying again.", exc_info=True)


def test_bundle_upload_directory(http_server, testdir):
    '''
    Uploading a directory requires that we turn it into an archive first.
    '''
    cut = HTTPBundleUploader(http_server.url)
    with open(p(testdir, 'random_file'), 'w') as f:
        f.write("smashing")

    cut(testdir)

    req = http_server.requests.get()
    while req['method'] != 'POST':
        req = http_server.requests.get()

    print(req)
    assert req['headers']['content-type'] == BUNDLE_ARCHIVE_MIME_TYPE


def test_bundle_upload_archive(http_server):
    pass
