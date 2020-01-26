from __future__ import print_function
import subprocess
from os.path import join as p
from os import makedirs, listdir
from pytest import mark, fixture
from contextlib import contextmanager
import transaction

from owmeta.command import DEFAULT_OWM_DIR as OD, OWM
from owmeta.context import Context

from rdflib.term import URIRef, Literal

from .TestUtilities import assertRegexpMatches, assertNotRegexpMatches
from .OWMCLITest import module_fixture as owm_cli_fixture


pytestmark = mark.owm_cli_test


def module_fixture():
    with contextmanager(owm_cli_fixture)() as data:
        # Make a bundle
        data.sh('owm init')
        yield data


self = fixture(module_fixture)


def test_load(self):
    owm_bundle = p('tests', 'bundle.tar.xz')
    self.sh('owm bundle load ' + owm_bundle)
    assertRegexpMatches(
        self.sh('owm bundle cache list'),
        r'archive_test_bundle'
    )


def test_install(self):
    '''
    Install a bundle and make sure we can use it with Bundle
    '''
    self.writefile('abundle.yml', '''\
    ---
    id: abundle
    description: I'm a description
    includes: ["http://example.org/test_ctx"]
    ''')
    with OWM(owmdir=p(self.testdir, OD)).connect() as conn:
        with transaction.manager:
            graph = conn.conf['rdf.graph']
            sg = graph.get_context('http://example.org/test_ctx')
            sg.add((URIRef('http://example.org/a'),
                    URIRef('http://example.org/b'),
                    Literal('c')))

    homedir = p(self.testdir, 'home')
    makedirs(homedir)
    self.sh('owm bundle register abundle.yml')
    print(self.sh('owm bundle install abundle',
        env={'HOME': homedir}))
    self.writefile('use.py', '''\
    from owmeta.bundle import Bundle
    from rdflib.term import URIRef, Literal
    with Bundle('abundle') as bnd:
        # "contextualize" the Context with the bundle to access contexts within the bundle
        print((URIRef('http://example.org/a'),
               URIRef('http://example.org/b'),
               Literal('c')) in bnd.rdf, end='')
    ''')
    assert self.sh('python use.py',
        env={'HOME': homedir}) == 'True'


def test_register(self):
    self.writefile('abundle.yml', '''\
    ---
    id: abundle
    description: I'm a description
    ''')
    self.sh('owm bundle register abundle.yml')
    assertRegexpMatches(
        self.sh('owm bundle list'),
        r'abundle - I\'m a description'
    )


def test_list_descriptor_removed(self):
    self.writefile('abundle.yml', '''\
    ---
    id: abundle
    description: I'm a description
    ''')
    self.sh('owm bundle register abundle.yml',
            'rm abundle.yml')
    assertRegexpMatches(
        self.sh('owm bundle list'),
        r"abundle - ERROR: Cannot read bundle descriptor at 'abundle.yml'"
    )


def test_list_descriptor_moved(self):
    self.writefile('abundle.yml', '''\
    ---
    id: abundle
    description: I'm a description
    ''')
    self.sh('owm bundle register abundle.yml',
            'mv abundle.yml bundle.yml')
    assertRegexpMatches(
        self.sh('owm bundle list'),
        r"abundle - ERROR: Cannot read bundle descriptor at 'abundle.yml'"
    )


def test_reregister(self):
    self.writefile('abundle.yml', '''\
    ---
    id: abundle
    description: I'm a description
    ''')
    self.sh('owm bundle register abundle.yml',
            'mv abundle.yml bundle.yml',
            'owm bundle register bundle.yml')
    assertRegexpMatches(
        self.sh('owm bundle list'),
        r"abundle - I'm a description"
    )


def test_cache_list(self):
    '''
    List bundles in the cache
    '''
    bundle_dir = p(self.test_homedir, '.owmeta', 'bundles',
                   'test%2Fmain', '1')
    makedirs(bundle_dir)
    with open(p(bundle_dir, 'manifest'), 'w') as mf:
        mf.write('{"version": 1, "id": "test/main"}')
    assertRegexpMatches(
        self.sh('owm bundle cache list'),
        r'test/main@1'
    )


def test_cache_list_empty(self):
    '''
    List bundles in the cache
    '''
    assert self.sh('owm bundle cache list') == ''


def test_cache_list_multiple_versions(self):
    '''
    List bundles in the cache.

    For the same bundle ID, they should be in reverse version order (newest versions
    first)
    '''
    bundle_dir1 = p(self.test_homedir, '.owmeta', 'bundles',
                   'test%2Fmain', '1')
    bundle_dir2 = p(self.test_homedir, '.owmeta', 'bundles',
                   'test%2Fmain', '2')
    makedirs(bundle_dir1)
    makedirs(bundle_dir2)
    with open(p(bundle_dir1, 'manifest'), 'w') as mf:
        mf.write('{"version": 1, "id": "test/main"}')
    with open(p(bundle_dir2, 'manifest'), 'w') as mf:
        mf.write('{"version": 2, "id": "test/main"}')
    assertRegexpMatches(
        self.sh('owm bundle cache list'),
        r'test/main@2\ntest/main@1'
    )


def test_cache_list_different_bundles(self):
    '''
    List bundles in the cache
    '''
    bundle_dir1 = p(self.test_homedir, '.owmeta', 'bundles',
                   'test%2Fmain', '1')
    bundle_dir2 = p(self.test_homedir, '.owmeta', 'bundles',
                   'test%2Fsecondary', '1')
    makedirs(bundle_dir1)
    makedirs(bundle_dir2)
    with open(p(bundle_dir1, 'manifest'), 'w') as mf:
        mf.write('{"version": 1, "id": "test/main"}')
    with open(p(bundle_dir2, 'manifest'), 'w') as mf:
        mf.write('{"version": 1, "id": "test/secondary"}')
    assertRegexpMatches(
        self.sh('owm bundle cache list'),
        r'test/main@1'
    )
    assertRegexpMatches(
        self.sh('owm bundle cache list'),
        r'test/secondary@1'
    )


def test_cache_list_version_check(self):
    '''
    bundle cache list filters out bundles with the wrong version
    '''
    bundle_dir1 = p(self.test_homedir, '.owmeta', 'bundles',
                   'test%2Fmain', '1')
    bundle_dir2 = p(self.test_homedir, '.owmeta', 'bundles',
                   'test%2Fsecondary', '2')
    makedirs(bundle_dir1)
    makedirs(bundle_dir2)
    with open(p(bundle_dir1, 'manifest'), 'w') as mf:
        mf.write('{"version": 1, "id": "test/main"}')
    with open(p(bundle_dir2, 'manifest'), 'w') as mf:
        mf.write('{"version": 1, "id": "test/secondary"}')
    assertRegexpMatches(
        self.sh('owm bundle cache list'),
        r'test/main@1'
    )
    assertNotRegexpMatches(
        self.sh('owm bundle cache list'),
        r'test/secondary@1'
    )


def test_cache_list_version_check_warning(self):
    '''
    bundle cache list filters out bundles with the wrong version
    '''
    bundle_dir1 = p(self.test_homedir, '.owmeta', 'bundles',
                   'test%2Fmain', '1')
    bundle_dir2 = p(self.test_homedir, '.owmeta', 'bundles',
                   'test%2Fsecondary', '2')
    makedirs(bundle_dir1)
    makedirs(bundle_dir2)
    with open(p(bundle_dir1, 'manifest'), 'w') as mf:
        mf.write('{"version": 1, "id": "test/main"}')
    with open(p(bundle_dir2, 'manifest'), 'w') as mf:
        mf.write('{"version": 1, "id": "test/secondary"}')
    output = self.sh('owm bundle cache list', stderr=subprocess.STDOUT)
    assertRegexpMatches(output, r'manifest.*match')


def test_cache_list_description(self):
    '''
    Make sure the bundle description shows up
    '''
    bundle_dir1 = p(self.test_homedir, '.owmeta', 'bundles',
                   'test%2Fmain', '1')
    makedirs(bundle_dir1)
    with open(p(bundle_dir1, 'manifest'), 'w') as mf:
        mf.write('{"version": 1, "id": "test/main", "description": "Waka waka"}')
    assertRegexpMatches(
        self.sh('owm bundle cache list'),
        r'Waka waka'
    )


def test_checkout(self):
    '''
    Checking out a bundle changes the set of graphs to the chosen bundle
    '''
    self.sh('owm bundle checkout test/main')
    # TODO: Add an assert


def test_deploy(self):
    self.sh('owm bundle deploy test/main')
    # TODO: Add an assert
