import tempfile
import six
import pytest
import os
import shutil
import sys
from os.path import join as p
from owmeta.file_match import match_directories, match_files


_glob_has_recursive = sys.version_info >= (3, 5)

glob_lacks_recursive = pytest.mark.skipif(_glob_has_recursive, reason='recursive iglob not supported before 3.5')
glob_has_recursive = pytest.mark.skipif(not _glob_has_recursive, reason='recursive iglob not supported before 3.5')


@pytest.fixture
def dirs():
    testdir = tempfile.mkdtemp(prefix=__name__ + '.')

    class helper(object):
        def __init__(self):
            self.dirs = dict()
            self.files = dict()
            self.base = testdir

        def __call__(self, dirlist=(), flist=()):
            for d in dirlist:
                self.dirs[d] = os.makedirs(p(testdir, d))

            for f in flist:
                self.files[f] = open(p(testdir, f), mode='w').close()
            return self

        def __getitem__(self, n):
            if isinstance(n, six.string_types):
                return self.dirs.get(n) or self.files.get(n)
            else:
                return tuple(self.dirs.get(m) or self.files.get(m) for m in n)

    try:
        yield helper()
    finally:
        shutil.rmtree(testdir)


def test_match_dir_1(dirs):
    ds = dirs(['a/b/c/d/e', 'a/q/m/d'])
    assert sum(1 for _ in match_directories(ds.base, 'a/*/*/d')) == 2


def test_match_dir_2(dirs):
    ds = dirs(['a/b/c/d/e', 'a/q/m/d'])
    assert len(list(match_directories(ds.base, 'a/*/*/*'))) == 2


@glob_has_recursive
def test_match_files_recursive_1(dirs):
    ds = dirs(['a/b/c'], ['a/b/c/f', 'a/b/g'])
    assert len(list(match_files(ds.base, 'a/**'))) == 2


@glob_has_recursive
def test_match_files_recursive_2(dirs):
    ds = dirs(['a/b/c/d', 'a/q/m/v'], ['a/b/c/d/e', 'a/q/m/v/d'])
    assert len(list(match_directories(ds.base, 'a/**/d'))) == 1


@glob_has_recursive
def test_match_directories_recursive(dirs):
    ds = dirs(['a/b/c/d/e', 'a/q/m/v/d'])
    assert len(list(match_directories(ds.base, 'a/**/d'))) == 2


@glob_lacks_recursive
def test_match_directories_recursive_fail(dirs):
    try:
        ds = dirs(['a/b/c/d/e', 'a/q/m/v/d'])
        match_directories(ds.base, 'a/**/d')
        assert False, "Should have errored out"
    except Exception:
        pass
