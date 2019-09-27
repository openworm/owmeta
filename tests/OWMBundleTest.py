from __future__ import print_function
from os.path import join as p
from os import makedirs
from pytest import mark, fixture
from contextlib import contextmanager
import transaction

from owmeta import connect
from owmeta.command import DEFAULT_OWM_DIR as OD
from owmeta.context import Context

from rdflib.term import URIRef, Literal

from .TestUtilities import assertRegexpMatches
from .OWMCLITest import module_fixture as owm_cli_fixture


pytestmark = mark.owm_cli_test


def module_fixture():
    with contextmanager(owm_cli_fixture)() as data:
        # Make a bundle
        data.sh('owm init')
        with open(p(OD, 'owm.conf'), 'r') as f:
            print(f.read())
        yield data


self = fixture(module_fixture)


def test_load(self):
    owm_bundle = p('tests', 'bundle.tar.gz')
    self.sh('owm bundle load ' + owm_bundle)
    assertRegexpMatches(
        self.sh('owm bundle index query'),
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
    with connect(p(OD, 'owm.conf')) as conn:
        with transaction.manager:
            graph = conn.conf['rdf.graph']
            sg = graph.get_context('http://example.org/test_ctx')
            sg.add((URIRef('a'), URIRef('b'), Literal('c')))

    self.sh('owm bundle register abundle.yml')
    self.sh('owm bundle install abundle')
    self.writefile('use.py', '''\
    from owmeta.bundle import Bundle
    from rdflib.term import URIRef, Literal
    with Bundle('abundle') as bnd:
        # "contextualize" the Context with the bundle to access contexts within the bundle
        print((URIRef('a'), URIRef('b'), Literal('c')) in bnd.rdf)
    ''')
    assert self.sh('python use.py') == 'True'


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


def test_fetch_and_query(self):
    '''
    Retrieve the bundle from wherever and make sure we can list it
    '''
    self.sh('owm bundle fetch openworm/main')
    assertRegexpMatches(
        self.sh('owm bundle index query'),
        r'openworm/main'
    )


def test_checkout(self):
    '''
    Checking out a bundle changes the set of graphs to the chosen bundle
    '''
    self.sh('owm bundle checkout openworm/main')
    # TODO: Add an assert


def test_deploy(self):
    self.sh('owm bundle deploy openworm/main')
    # TODO: Add an assert
