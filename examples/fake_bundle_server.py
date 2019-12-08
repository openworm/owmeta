import sys
from os.path import join as p
from os import mkdir, listdir, chdir
import tarfile
import logging
from multiprocessing import Process
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json

import requests

from owmeta import connect
from owmeta.dataObject import DataObject, DatatypeProperty
from owmeta.context import Context
from owmeta.bundle import Bundle, Descriptor, make_include_func, Installer

try:
    from tempfile import TemporaryDirectory
except ImportError:
    from backports.tempfile import TemporaryDirectory

L = logging.getLogger(__name__)


class A(DataObject):
    redness = DatatypeProperty()
    blueness = DatatypeProperty()


def wait_for_started(server_addr):
    done = False
    while not done:
        try:
            requests.head('http://{}:{}'.format(*server_addr))
            done = True
        except Exception:
            L.info("Unable to connect to the bundle server. Trying again.", exc_info=True)


def start():
    tempdir = TemporaryDirectory('example_bundle_dir')
    server, srvdir = setUp(tempdir.name)
    L.info("starting server")

    def pfunc():
        chdir(srvdir)
        server.serve_forever()

    p = Process(target=pfunc)
    p.start()

    def shutdown():
        L.info("shutting down...")
        p.terminate()
        L.info("server shut down. waiting for process to die...")
        p.join()
        L.info("process dead. cleaning up temporary directory...")
        tempdir.cleanup()
        L.info("directory cleaned. shutdown complete.")

    return server, shutdown


def setUp(base):
    with connect({'rdf.source': 'sqlite',
                  'rdf.store_conf': p(base, 'bundle.db')}) as conn:
        ctx0 = conn(Context)('https://example.org/bundles#example')

        a = ctx0(A)(ident='http://example.org/A')
        a.redness(24)
        a.blueness(24)

        ctx0.save()

        desc = Descriptor('example/aBundle')
        desc.name = 'A Bundle'
        desc.version = 23
        desc.description = 'An example bundle'
        desc.includes = set([make_include_func('https://example.org/bundles#example')])

        rdf = conn.conf['rdf.graph']
        srcdir = p(base, 'install_dir')
        mkdir(srcdir)

        bnddir = p(base, 'bundles_dir')
        mkdir(bnddir)

        srvdir = p(base, 'server_directory')
        mkdir(srvdir)

        bi = Installer(srcdir, bnddir, rdf)
        install_dir = bi.install(desc)

        with tarfile.open(p(srvdir, 'example_bundle.tar.xz'), mode='w:xz') as ba:
            # arcname='.' removes the leading part of the path to the install directory
            ba.add(install_dir, arcname='.')
        return make_server(), srvdir


def make_server():
    class _Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/bundles.idx':
                base_uri = self._get_base_uri()
                self.send_response(200)
                self.send_header('content-type', 'application/json')
                self.end_headers()
                body = json.dumps({
                    'example/aBundle': {
                        23: base_uri + '/example_bundle.tar.xz'
                    }
                })
                # cannot write directly to wfile with json.dump because it only outputs
                # strings :(
                self.wfile.write(body.encode('UTF-8'))
            else:
                super(_Handler, self).do_GET()

        def _get_base_uri(self):
            return 'http://{}:{}'.format(*self.server.server_address)

        def do_POST(self):
            if self.path.endswith('SHUTDOWN'):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'\n\n')
            else:
                super(_Handler, self).do_POST()

    port = 8000
    while True:
        try:
            return HTTPServer(('127.0.0.1', port), _Handler)
        except OSError as e:
            if e.errno != 98:
                raise
            port += 1


if __name__ == '__main__':
    server_address_file = sys.argv[1]
    logging.basicConfig(level=logging.INFO)
    server, shutdown = start()
    wait_for_started(server.server_address)
    with open(server_address_file, 'w') as f:
        print('http://{}:{}'.format(*server.server_address), file=f)
    L.info('started')