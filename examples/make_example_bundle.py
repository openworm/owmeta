from os.path import join as p
from os import mkdir, stat
import tarfile
import json
import rdflib
from owmeta import connect
from owmeta.dataObject import DataObject, DatatypeProperty
from owmeta.context import Context
from owmeta.bundle import Bundle, Descriptor, make_include_func, Installer
from http.server import HTTPServer, SimpleHTTPRequestHandler

try:
    from tempfile import TemporaryDirectory, mkdtemp
except ImportError:
    from backports.tempfile import TemporaryDirectory, mkdtemp


class A(DataObject):
    redness = DatatypeProperty()
    blueness = DatatypeProperty()


def main():
    with TemporaryDirectory() as base:
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

            # TODO: create a special handler for serving up the index file with the
            # server's URLs

            with open(p(srvdir, 'example_bundle.tar.xz'), 'wb') as out:
                with tarfile.open(mode='w:xz', fileobj=out) as ba:
                    ba.add(install_dir)
            run_server(srvdir)


def run_server(basedir):
    HC = type('Handler', (SimpleHTTPRequestHandler,), dict(directory=basedir))

    done = False
    port = 8888
    while not done:
        try:
            with HTTPServer(('127.0.0.1', port), HC) as httpd:
                print("Serving bundles on port %d" % port)
                httpd.serve_forever()
        except OSError as e:
            if e.errno != 98:
                done = True
            port += 1

    done = True


if __name__ == '__main__':
    main()
