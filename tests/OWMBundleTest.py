from __future__ import print_function
from os.path import join as p
from pytest import mark, fixture
from contextlib import contextmanager
from .TestUtilities import assertRegexpMatches
from .OWMCLITest import module_fixture as owm_cli_fixture


pytestmark = mark.owm_cli_test


def module_fixture():
    with contextmanager(owm_cli_fixture)() as data:
        # Make a bundle
        data.bundle_name = 'http://example.org/test_bundle'
        yield data


self = fixture(module_fixture)


def test_load(self):
    owm_bundle = p('tests', 'bundle.tar.gz')
    self.sh('owm bundle load ' + owm_bundle)
    assertRegexpMatches(
        self.sh('owm bundle repo query'),
        r'http://example.org/archive_test_bundle'
    )


def test_register(self):
    self.sh('owm bundle register http://example.org/')


def test_fetch_and_query(self):
    '''
    Retrieve the bundle from wherever and make sure we can list it
    '''
    self.sh('owm bundle fetch http://openworm.org/data#main')
    assertRegexpMatches(
        self.sh('owm bundle repo query'),
        r'http://openworm.org/data#main'
    )


def test_checkout(self):
    '''
    Checking out a bundle changes the set of graphs to the chosen bundle
    '''
    self.sh('owm bundle checkout http://openworm.org/data#main')
    # TODO: Add an assert


def test_deploy(self):
    self.sh('owm bundle deploy http://openworm.org/data#main')
    # TODO: Add an assert
