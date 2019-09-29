from multiprocessing import Process
try:
    from tempfile import TemporaryDirectory
except ImportError:
    from backports.tempfile import TemporaryDirectory
import rdflib
import transaction
from collections import namedtuple
from rdflib.term import Literal, URIRef
from owmeta.bundle import Installer, Descriptor, make_include_func, FilesDescriptor
from os.path import join as p, isdir, isfile
from os import listdir

import pytest


Data = namedtuple('S', ('source_directory', 'bundles_directory'))


@pytest.fixture
def dirs():
    with TemporaryDirectory() as source_directory,\
            TemporaryDirectory() as bundles_directory:
        yield Data(source_directory, bundles_directory)


def test_bundle_install_directory(dirs):
    d = Descriptor('test')
    bi = Installer(*dirs, graph=rdflib.ConjunctiveGraph())
    bi.install(d)
    assert isdir(p(dirs.bundles_directory, 'test'))


def test_context_hash_file_exists(dirs):
    d = Descriptor('test')
    ctxid = 'http://example.org/ctx1'
    d.includes.add(make_include_func(ctxid))
    g = rdflib.ConjunctiveGraph()
    cg = g.get_context(ctxid)
    cg.add((URIRef('a'), URIRef('b'), URIRef('c')))
    bi = Installer(*dirs, graph=g)
    bi.install(d)
    assert isfile(p(dirs.bundles_directory, 'test', 'graphs', 'hashes'))


def test_context_index_file_exists(dirs):
    d = Descriptor('test')
    ctxid = 'http://example.org/ctx1'
    d.includes.add(make_include_func(ctxid))
    g = rdflib.ConjunctiveGraph()
    cg = g.get_context(ctxid)
    cg.add((URIRef('a'), URIRef('b'), URIRef('c')))
    bi = Installer(*dirs, graph=g)
    bi.install(d)
    assert isfile(p(dirs.bundles_directory, 'test', 'graphs', 'index'))


def test_context_hash_file_contains_ctxid(dirs):
    d = Descriptor('test')
    ctxid = 'http://example.org/ctx1'
    d.includes.add(make_include_func(ctxid))
    g = rdflib.ConjunctiveGraph()
    cg = g.get_context(ctxid)
    with transaction.manager:
        cg.add((URIRef('a'), URIRef('b'), URIRef('c')))
    bi = Installer(*dirs, graph=g)
    bi.install(d)
    with open(p(dirs.bundles_directory, 'test', 'graphs', 'hashes'), 'rb') as f:
        assert f.read().startswith(ctxid.encode('UTF-8'))


def test_context_index_file_contains_ctxid(dirs):
    d = Descriptor('test')
    ctxid = 'http://example.org/ctx1'
    d.includes.add(make_include_func(ctxid))
    g = rdflib.ConjunctiveGraph()
    cg = g.get_context(ctxid)
    with transaction.manager:
        cg.add((URIRef('a'), URIRef('b'), URIRef('c')))
    bi = Installer(*dirs, graph=g)
    bi.install(d)
    with open(p(dirs.bundles_directory, 'test', 'graphs', 'index'), 'rb') as f:
        assert f.read().startswith(ctxid.encode('UTF-8'))


def test_multiple_context_hash(dirs):
    d = Descriptor('test')
    ctxid_1 = 'http://example.org/ctx1'
    ctxid_2 = 'http://example.org/ctx2'
    d.includes.add(make_include_func(ctxid_1))
    d.includes.add(make_include_func(ctxid_2))
    g = rdflib.ConjunctiveGraph()
    cg = g.get_context(ctxid_1)
    with transaction.manager:
        cg.add((URIRef('a'), URIRef('b'), URIRef('c')))

    cg = g.get_context(ctxid_2)
    with transaction.manager:
        cg.add((URIRef('a'), URIRef('b'), URIRef('c')))

    bi = Installer(*dirs, graph=g)
    bi.install(d)
    with open(p(dirs.bundles_directory, 'test', 'graphs', 'hashes'), 'rb') as f:
        contents = f.read()
        assert ctxid_1.encode('UTF-8') in contents
        assert ctxid_2.encode('UTF-8') in contents


def test_no_dupe(dirs):
    d = Descriptor('test')
    ctxid_1 = 'http://example.org/ctx1'
    ctxid_2 = 'http://example.org/ctx2'
    d.includes.add(make_include_func(ctxid_1))
    d.includes.add(make_include_func(ctxid_2))
    g = rdflib.ConjunctiveGraph()
    cg = g.get_context(ctxid_1)
    with transaction.manager:
        cg.add((URIRef('a'), URIRef('b'), URIRef('c')))

    cg = g.get_context(ctxid_2)
    with transaction.manager:
        cg.add((URIRef('a'), URIRef('b'), URIRef('c')))

    bi = Installer(*dirs, graph=g)
    bi.install(d)
    graph_files = [x for x in listdir(p(dirs.bundles_directory, 'test', 'graphs')) if x.endswith('.nt')]
    assert len(graph_files) == 1


def test_file_copy(dirs):
    d = Descriptor('test')
    open(p(dirs[0], 'somefile'), 'w').close()
    d.files = FilesDescriptor()
    d.files.includes.add('somefile')
    g = rdflib.ConjunctiveGraph()
    bi = Installer(*dirs, graph=g)
    bi.install(d)
    bfiles = p(dirs.bundles_directory, 'test', 'files')
    assert set(listdir(bfiles)) == set(['hashes', 'somefile'])


def test_file_pattern_copy(dirs):
    d = Descriptor('test')
    open(p(dirs[0], 'somefile'), 'w').close()
    d.files = FilesDescriptor()
    d.files.patterns.add('some*')
    g = rdflib.ConjunctiveGraph()
    bi = Installer(*dirs, graph=g)
    bi.install(d)
    bfiles = p(dirs.bundles_directory, 'test', 'files')
    assert set(listdir(bfiles)) == set(['hashes', 'somefile'])


def test_file_hash(dirs):
    d = Descriptor('test')
    open(p(dirs[0], 'somefile'), 'w').close()
    d.files = FilesDescriptor()
    d.files.includes.add('somefile')
    g = rdflib.ConjunctiveGraph()
    bi = Installer(*dirs, graph=g)
    bi.install(d)
    assert isfile(p(dirs.bundles_directory, 'test', 'files', 'hashes'))


def test_file_hash_content(dirs):
    d = Descriptor('test')
    open(p(dirs[0], 'somefile'), 'w').close()
    d.files = FilesDescriptor()
    d.files.includes.add('somefile')
    g = rdflib.ConjunctiveGraph()
    bi = Installer(*dirs, graph=g)
    bi.install(d)
    with open(p(dirs.bundles_directory, 'test', 'files', 'hashes'), 'rb') as f:
        contents = f.read()
        assert b'somefile' in contents
