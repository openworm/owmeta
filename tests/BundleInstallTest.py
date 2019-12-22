from multiprocessing import Process
try:
    from tempfile import TemporaryDirectory
except ImportError:
    from backports.tempfile import TemporaryDirectory
import rdflib
import transaction
from collections import namedtuple
from rdflib.term import Literal, URIRef
from owmeta.bundle import (Installer, Descriptor, make_include_func, FilesDescriptor,
                           MissingImports)
from owmeta.context_common import CONTEXT_IMPORTS
from os.path import join as p, isdir, isfile
from os import listdir

import pytest


Dirs = namedtuple('Dirs', ('source_directory', 'bundles_directory'))


@pytest.fixture
def dirs():
    with TemporaryDirectory() as source_directory,\
            TemporaryDirectory() as bundles_directory:
        yield Dirs(source_directory, bundles_directory)


def test_bundle_install_directory(dirs):
    d = Descriptor('test')
    bi = Installer(*dirs, graph=rdflib.ConjunctiveGraph())
    bi.install(d)
    assert isdir(p(dirs.bundles_directory, 'test', '1'))


def test_context_hash_file_exists(dirs):
    d = Descriptor('test')
    ctxid = 'http://example.org/ctx1'
    d.includes.add(make_include_func(ctxid))
    g = rdflib.ConjunctiveGraph()
    cg = g.get_context(ctxid)
    cg.add((URIRef('a'), URIRef('b'), URIRef('c')))
    bi = Installer(*dirs, graph=g)
    bi.install(d)
    assert isfile(p(dirs.bundles_directory, 'test', '1', 'graphs', 'hashes'))


def test_context_index_file_exists(dirs):
    d = Descriptor('test')
    ctxid = 'http://example.org/ctx1'
    d.includes.add(make_include_func(ctxid))
    g = rdflib.ConjunctiveGraph()
    cg = g.get_context(ctxid)
    cg.add((URIRef('a'), URIRef('b'), URIRef('c')))
    bi = Installer(*dirs, graph=g)
    bi.install(d)
    assert isfile(p(dirs.bundles_directory, 'test', '1', 'graphs', 'index'))


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
    with open(p(dirs.bundles_directory, 'test', '1', 'graphs', 'hashes'), 'rb') as f:
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
    with open(p(dirs.bundles_directory, 'test', '1', 'graphs', 'index'), 'rb') as f:
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
    with open(p(dirs.bundles_directory, 'test', '1', 'graphs', 'hashes'), 'rb') as f:
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

    graph_files = [x for x in listdir(p(dirs.bundles_directory, 'test', '1', 'graphs')) if x.endswith('.nt')]
    assert len(graph_files) == 1


def test_file_copy(dirs):
    d = Descriptor('test')
    open(p(dirs[0], 'somefile'), 'w').close()
    d.files = FilesDescriptor()
    d.files.includes.add('somefile')
    g = rdflib.ConjunctiveGraph()
    bi = Installer(*dirs, graph=g)
    bi.install(d)
    bfiles = p(dirs.bundles_directory, 'test', '1', 'files')
    assert set(listdir(bfiles)) == set(['hashes', 'somefile'])


def test_file_pattern_copy(dirs):
    d = Descriptor('test')
    open(p(dirs[0], 'somefile'), 'w').close()
    d.files = FilesDescriptor()
    d.files.patterns.add('some*')
    g = rdflib.ConjunctiveGraph()
    bi = Installer(*dirs, graph=g)
    bi.install(d)
    bfiles = p(dirs.bundles_directory, 'test', '1', 'files')
    assert set(listdir(bfiles)) == set(['hashes', 'somefile'])


def test_file_hash(dirs):
    d = Descriptor('test')
    open(p(dirs[0], 'somefile'), 'w').close()
    d.files = FilesDescriptor()
    d.files.includes.add('somefile')
    g = rdflib.ConjunctiveGraph()
    bi = Installer(*dirs, graph=g)
    bi.install(d)
    assert isfile(p(dirs.bundles_directory, 'test', '1', 'files', 'hashes'))


def test_file_hash_content(dirs):
    d = Descriptor('test')
    open(p(dirs[0], 'somefile'), 'w').close()
    d.files = FilesDescriptor()
    d.files.includes.add('somefile')
    g = rdflib.ConjunctiveGraph()
    bi = Installer(*dirs, graph=g)
    bi.install(d)
    with open(p(dirs.bundles_directory, 'test', '1', 'files', 'hashes'), 'rb') as f:
        contents = f.read()
        assert b'somefile' in contents


def test_imports_are_included(dirs):
    '''
    If we have imports and no dependencies, then thrown an exception if we have not
    included them in the bundle
    '''
    imports_ctxid = 'http://example.org/imports'
    ctxid_1 = 'http://example.org/ctx1'
    ctxid_2 = 'http://example.org/ctx2'

    # Make a descriptor that includes ctx1 and the imports, but not ctx2
    d = Descriptor('test')
    d.includes.add(make_include_func(ctxid_1))
    d.includes.add(make_include_func(imports_ctxid))

    # Add some triples so the contexts aren't empty -- we can't save an empty context
    g = rdflib.ConjunctiveGraph()
    cg_1 = g.get_context(ctxid_1)
    cg_2 = g.get_context(ctxid_2)
    cg_imp = g.get_context(imports_ctxid)
    with transaction.manager:
        cg_1.add((URIRef('a'), URIRef('b'), URIRef('c')))
        cg_2.add((URIRef('d'), URIRef('e'), URIRef('f')))
        cg_imp.add((URIRef(ctxid_1), CONTEXT_IMPORTS, URIRef(ctxid_2)))

    bi = Installer(*dirs, imports_ctx=imports_ctxid, graph=g)
    with pytest.raises(MissingImports):
        bi.install(d)


def test_imports_in_dependencies(dirs):
    '''
    If we have imports and a dependency includes the context, then we shouldn't have an
    error
    '''
    imports_ctxid = 'http://example.org/imports'
    ctxid_1 = 'http://example.org/ctx1'
    ctxid_2 = 'http://example.org/ctx2'

    # Make a descriptor that includes ctx1 and the imports, but not ctx2
    d = Descriptor('test')
    d.includes.add(make_include_func(ctxid_1))
    d.includes.add(make_include_func(imports_ctxid))
    d.dependencies.add(DependencyDescriptor('example'))

    # Add some triples so the contexts aren't empty -- we can't save an empty context
    g = rdflib.ConjunctiveGraph()
    cg_1 = g.get_context(ctxid_1)
    cg_2 = g.get_context(ctxid_2)
    cg_imp = g.get_context(imports_ctxid)
    with transaction.manager:
        cg_1.add((URIRef('a'), URIRef('b'), URIRef('c')))
        cg_2.add((URIRef('d'), URIRef('e'), URIRef('f')))
        cg_imp.add((URIRef(ctxid_1), CONTEXT_IMPORTS, URIRef(ctxid_2)))

    bi = Installer(*dirs, imports_ctx=imports_ctxid, graph=g)
    with pytest.raises(MissingImports):
        bi.install(d)
