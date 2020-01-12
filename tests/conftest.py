from pytest import fixture
import tempfile


@fixture
def tempdir():
    with tempfile.TemporaryDirectory(prefix=__name__ + '.') as td:
        yield td
