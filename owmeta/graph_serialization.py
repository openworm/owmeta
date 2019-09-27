'''
Utilies for graph serialization
'''
import hashlib
from rdflib import plugin
from rdflib.serializer import Serializer
from os.path import join as p, exists


def write_canonical_to_file(graph, file_name):
    with open(file_name, 'wb') as f:
        write_canonical(graph, f)


def write_canonical(graph, out):
    serializer = plugin.get('nt', Serializer)(sorted(graph))
    serializer.serialize(out)


def gen_ctx_fname(ident, base_directory, hashfunc=None):
    hs = (hashfunc or hashlib.sha256)(ident.encode('UTF-8')).hexdigest()
    fname = p(base_directory, hs + '.nt')
    i = 1
    while exists(fname):
        fname = p(base_directory, hs + '-' + str(i) + '.nt')
        i += 1
    return fname
