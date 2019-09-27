from multiprocessing import Process
try:
    from tempfile import TemporaryDirectory
except ImportError:
    from backports.tempfile import TemporaryDirectory
import rdflib
import transaction
from rdflib.term import Literal, URIRef
from owmeta.bundle import Installer, Descriptor, make_include_func, FilesDescriptor
from os.path import join as p, isdir, isfile
from os import listdir

import pytest


@pytest.fixture
def directories():
    with TemporaryDirectory() as source_directory,\
            TemporaryDirectory() as index_directory,\
            TemporaryDirectory() as bundles_directory:
        yield source_directory, index_directory, bundles_directory


def test_bundle_install_directory(directories):
    d = Descriptor('test')
    bi = Installer(*directories, graph=rdflib.ConjunctiveGraph())
    bi.install(d)
    assert isdir(p(directories[2], 'test'))


def test_context_hash_file_exists(directories):
    d = Descriptor('test')
    ctxid = 'http://example.org/ctx1'
    d.includes.add(make_include_func(ctxid))
    g = rdflib.ConjunctiveGraph()
    cg = g.get_context(ctxid)
    cg.add((URIRef('a'), URIRef('b'), URIRef('c')))
    bi = Installer(*directories, graph=g)
    bi.install(d)
    assert isfile(p(directories[2], 'test', 'graphs', 'hashes'))


def test_context_hash_file_contains_ctx_hash(directories):
    d = Descriptor('test')
    ctxid = 'http://example.org/ctx1'
    d.includes.add(make_include_func(ctxid))
    g = rdflib.ConjunctiveGraph()
    cg = g.get_context(ctxid)
    with transaction.manager:
        cg.add((URIRef('a'), URIRef('b'), URIRef('c')))
    bi = Installer(*directories, graph=g)
    bi.install(d)
    with open(p(directories[2], 'test', 'graphs', 'hashes'), 'rb') as f:
        assert f.read().startswith(ctxid)


def test_multiple_context_hash(directories):
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

    bi = Installer(*directories, graph=g)
    bi.install(d)
    with open(p(directories[2], 'test', 'graphs', 'hashes'), 'rb') as f:
        contents = f.read()
        assert ctxid_1 in contents
        assert ctxid_2 in contents


def test_no_dupe(directories):
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

    bi = Installer(*directories, graph=g)
    bi.install(d)
    graph_files = [x for x in listdir(p(directories[2], 'test', 'graphs')) if x.endswith('.nt')]
    assert len(graph_files) == 1


def test_file_copy(directories):
    d = Descriptor('test')
    open(p(directories[0], 'somefile'), 'w').close()
    d.files = FilesDescriptor()
    d.files.includes.add('somefile')
    g = rdflib.ConjunctiveGraph()
    bi = Installer(*directories, graph=g)
    bi.install(d)
    bfiles = p(directories[2], 'test', 'files')
    assert set(listdir(bfiles)) == set(['hashes', 'somefile'])


def test_file_pattern_copy(directories):
    d = Descriptor('test')
    open(p(directories[0], 'somefile'), 'w').close()
    d.files = FilesDescriptor()
    d.files.patterns.add('some*')
    g = rdflib.ConjunctiveGraph()
    bi = Installer(*directories, graph=g)
    bi.install(d)
    bfiles = p(directories[2], 'test', 'files')
    assert set(listdir(bfiles)) == set(['hashes', 'somefile'])


def test_file_hash(directories):
    d = Descriptor('test')
    open(p(directories[0], 'somefile'), 'w').close()
    d.files = FilesDescriptor()
    d.files.includes.add('somefile')
    g = rdflib.ConjunctiveGraph()
    bi = Installer(*directories, graph=g)
    bi.install(d)
    assert isfile(p(directories[2], 'test', 'files', 'hashes'))


def test_file_hash_content(directories):
    d = Descriptor('test')
    open(p(directories[0], 'somefile'), 'w').close()
    d.files = FilesDescriptor()
    d.files.includes.add('somefile')
    g = rdflib.ConjunctiveGraph()
    bi = Installer(*directories, graph=g)
    bi.install(d)
    with open(p(directories[2], 'test', 'files', 'hashes'), 'rb') as f:
        contents = f.read()
        assert 'somefile' in contents
