from __future__ import print_function
from pytest import mark, fixture
from contextlib import contextmanager
from .POWCLITest import module_fixture as pow_cli_fixture


pytestmark = mark.pow_cli_test


def module_fixture():
    with contextmanager(pow_cli_fixture()) as data:
        # Make a bundle
        data.bundle_name = 'http://example.org/test_bundle'
        yield data


self = fixture(module_fixture)


def test_load(self):
    pow_bundle = p('tests', 'bundle.tar.gz')
    self.sh('pow bundle load ' + pow_bundle)
    assertRegexpMatches(
        self.sh('pow bundle list'),
        r'http://example.org/archive_test_bundle'
    )


def test_fetch_and_list(self):
    '''
    Retrieve the bundle from wherever and make sure we can list it
    '''
    self.sh('pow bundle fetch http://openworm.org/data#main')
    assertRegexpMatches(
        self.sh('pow bundle list'),
        r'http://openworm.org/data#main'
    )


def test_checkout(self):
    '''
    Checking out a bundle changes the set of graphs to the chosen bundle
    '''
    self.sh('pow bundle checkout http://openworm.org/data#main')
    assertRegexpMatches(
        self.sh('pow bundle list'),
        r'http://openworm.org/data#main'
    )


def test_deploy(self):
    '''
    Checking out a bundle changes the set of graphs to the chosen bundle
    '''
    self.sh('pow bundle deploy http://openworm.org/data#main')
    assertRegexpMatches(
        self.sh('pow bundle list'),
        r'http://openworm.org/data#main'
    )
