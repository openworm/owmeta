import os
from os.path import join as p
import json
import tempfile
import shutil

import rdflib
from rdflib import ConjunctiveGraph, URIRef
from pytest import fixture, raises

from owmeta.bundle import (NoRemoteAvailable,
                           Remote,
                           Deployer,
                           Descriptor,
                           Installer,
                           NotABundlePath)


@fixture
def testdir():
    testdir = tempfile.mkdtemp(prefix=__name__ + '.')
    try:
        yield testdir
    finally:
        shutil.rmtree(testdir)


@fixture
def bundle():
    res = BundleData()
    res.testdir = tempfile.mkdtemp(prefix=__name__ + '.')
    res.test_homedir = p(res.testdir, 'homedir')
    res.bundle_source_directory = p(res.testdir, 'bundle_source')
    res.bundles_directory = p(res.testdir, 'homedir', 'bundles')
    os.mkdir(res.test_homedir)
    os.mkdir(res.bundle_source_directory)
    os.mkdir(res.bundles_directory)

    # This is a bit of an integration test since it would be a PITA to maintain the bundle
    # format separately from the installer
    res.descriptor = Descriptor('test')
    graph = ConjunctiveGraph()
    ctxg = graph.get_context(URIRef('http://example.org/ctx'))
    ctxg.add((URIRef('http://example.org/a'),
              URIRef('http://example.org/b'),
              URIRef('http://example.org/c')))
    res.installer = Installer(
            res.bundle_source_directory,
            res.bundles_directory,
            graph=graph)
    res.bundle_directory = res.installer.install(res.descriptor)
    try:
        yield res
    finally:
        shutil.rmtree(res.testdir)


class BundleData(object):
    pass


def test_bundle_path_does_not_exist(testdir):
    ''' Can't deploy a bundle we don't have '''
    cut = Deployer()
    with raises(NotABundlePath):
        cut.deploy(p(testdir, 'notabundle'))


def test_bundle_directory_lacks_manifest(testdir):
    ''' A valid bundle needs a manifest '''

    cut = Deployer()
    os.mkdir(p(testdir, 'notabundle'))
    with raises(NotABundlePath):
        cut.deploy(p(testdir, 'notabundle'))


def test_bundle_directory_manifest_not_a_file(testdir):
    ''' A valid bundle manifest is a file '''

    cut = Deployer()
    os.makedirs(p(testdir, 'notabundle', 'manifest'))
    with raises(NotABundlePath):
        cut.deploy(p(testdir, 'notabundle'))


def test_bundle_directory_manifest_has_no_version(testdir):
    '''
    A valid bundle manifest has a version number, up to a specific version, all other
    fields are optional
    '''
    cut = Deployer()
    bdir = p(testdir, 'notabundle')
    os.makedirs(bdir)
    with open(p(bdir, 'manifest'), 'w') as mf:
        json.dump({}, mf)
    with raises(NotABundlePath):
        cut.deploy(p(testdir, 'notabundle'))


def test_bundle_directory_manifest_has_no_bundle_version(testdir):
    '''
    A valid bundle manifest has a version number, up to a specific version, all other
    fields are optional
    '''
    cut = Deployer()
    bdir = p(testdir, 'notabundle')
    os.makedirs(bdir)
    with open(p(bdir, 'manifest'), 'w') as mf:
        json.dump({'manifest_version': 1}, mf)
    with raises(NotABundlePath):
        cut.deploy(p(testdir, 'notabundle'))


def test_bundle_directory_manifest_has_no_bundle_id(testdir):
    '''
    A valid bundle manifest has a version number, up to a specific version, all other
    fields are optional
    '''
    cut = Deployer()
    bdir = p(testdir, 'notabundle')
    os.makedirs(bdir)
    with open(p(bdir, 'manifest'), 'w') as mf:
        json.dump({'manifest_version': 1, 'version': 1}, mf)
    with raises(NotABundlePath):
        cut.deploy(p(testdir, 'notabundle'))


def test_deploy_directory_from_installer(bundle):
    ''' Test that we can deploy an installed bundle '''

    rem = Remote('remote')
    Deployer().deploy(
        bundle.bundle_directory,
        remotes=(rem,)
    )


def test_deploy_directory_no_remotes(bundle):
    ''' We can't deploy if we don't have any remotes '''
    with raises(NoRemoteAvailable):
        Deployer().deploy(bundle.bundle_directory)


def test_deploy_directory_ignore_archive_only_remotes():
    '''
    Deploy can deploy directories or archives. A remote that doesn't allow.
    '''


def test_deploy_archive_ignore_directory_only_remotes():
    ''' Deploy can deploy directories or archives. '''
