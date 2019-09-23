from os.path import join, isdir, isfile
from glob import iglob
from six import PY2


def _match(basedir, pattern):
    pat = join(basedir, pattern)
    if '**' in pattern:
        if PY2:
            raise Exception('Recursive patterns are not supported in Python 2.7')
        return iglob(pat, recursive=True)
    return iglob(pat)


def match_directories(basedir, pattern):
    for m in _match(basedir, pattern):
        if isdir(m):
            yield m


def match_files(basedir, pattern):
    for m in _match(basedir, pattern):
        if isfile(m):
            yield m
