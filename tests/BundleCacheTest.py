from owmeta.bundle import Cache
from os.path import join as p
from os import makedirs
import tempfile


def test_cache_list_empty_dir():
    with tempfile.TemporaryDirectory(prefix=__name__ + '.') as tempdir:
        cut = Cache(tempdir)
        assert len(list(cut.list())) == 0


def test_cache_list_empty_no_versions():
    with tempfile.TemporaryDirectory(prefix=__name__ + '.') as tempdir:
        makedirs(p(tempdir, 'bdir'))
        cut = Cache(tempdir)
        assert len(list(cut.list())) == 0


def test_cache_list_empty_no_manifest():
    with tempfile.TemporaryDirectory(prefix=__name__ + '.') as tempdir:
        makedirs(p(tempdir, 'bdir', '10'))
        cut = Cache(tempdir)
        assert len(list(cut.list())) == 0


def test_cache_list_empty_malformed_manifest():
    with tempfile.TemporaryDirectory(prefix=__name__ + '.') as tempdir:
        bdir = p(tempdir, 'bdir', '10')
        makedirs(bdir)
        with open(p(bdir, 'manifest'), 'w') as f:
            f.write('certainly not a manifest')
        cut = Cache(tempdir)
        assert len(list(cut.list())) == 0


def test_cache_list_empty_inconsistent_manifest_1():
    with tempfile.TemporaryDirectory(prefix=__name__ + '.') as tempdir:
        bdir = p(tempdir, 'bdir', '10')
        makedirs(bdir)
        with open(p(bdir, 'manifest'), 'w') as f:
            f.write('{}')
        cut = Cache(tempdir)
        assert len(list(cut.list())) == 0
