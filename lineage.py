from PyOpenWorm import Data,Configureable
from xlrd import open_workbook
from rdflib import Literal, URIRef, Graph,Namespace,RDFS
import re
import httplib as H
from itertools import chain
from os import getcwd
# Read in from the spreadsheet
# leading substring
# matched names in first column go in an array
# Assert that the development name is actually unique
def read(n,sheet_number,cols,start=1):
    rb = open_workbook(n)
    for row in range(start,rb.sheet_by_index(sheet_number).nrows):
        l = []
        for i in range(cols):
            l.append(str(rb.sheet_by_index(sheet_number).cell(row,i).value))
        yield l

# Replace spaces with dots
postembryonic_regex = re.compile(r"^([A-Z0-9]+)\.([a-z]+)$")
embryonic_regex = re.compile(r"^([A-Z0-9]+) ([a-z]+)$")
goodname_regex = re.compile(r"^([A-Z0-9]+)(:?[. ]([a-z]+))?$")
nospace_regex = re.compile(r"^([A-Z0-9]+)([a-z]+)$")
# expression for
def normalize_lineage_name(name):
    n = str(name)

    if "," in n:
        parts = n.split(",")
        if len(parts) > 0:
            n = parts[0]
    n = n.strip()


    # find the starting substring with capitals and ensure there's a space after
    m = re.match(nospace_regex, n)
    if m:
        n = str(m.group(1)) +" "+ str(m.group(2))

    return n

def normalize(s):
    for i in s:
        n = normalize_lineage_name(i)
        yield n

def urlize(s,ns):
    s = s.replace(" ", "_")
    return ns[s]

def bad_names(names):
    for n in names:
        if not re.match(goodname_regex,n):
            yield n

def good_names(names):
    for n in names:
        if re.match(goodname_regex,n):
            yield n

def filter_lineage_slash(i):
    for k in i:
        if '/' in k[1]:
            yield k

def triple_adult_dev_mapping():
    sheet = read("lineage.xls",sheet_number=2, cols=3, start=2)
    for r in sheet:
        yield (r[0], "development_name", r[1])

def triple_dev_tree():
    sheet = read("lineage.xls",sheet_number=1, cols=6, start=2)
    for r in sheet:
        yield (r[0], "daughter_of", r[4])

#def missing_mappings():
    #a = set([r[0] for r in triple_dev_tree()])
    #a |= set([r[2] for r in triple_dev_tree()])
    #b = set([r[2] for r in triple_adult_dev_mapping()])
    #return (a - b, b - a)

def subject(s):
    for i in s:
        yield i[0]

def object(s):
    for i in s:
        yield i[2]

def smap_o(s,f):
    m = f(object(s))
    for i in zip(s,m):
        i[2] = m
        yield i

def all_bad_names():
    collector = set([])
    names = chain(subject(triple_dev_tree()), object(triple_dev_tree()), object(triple_adult_dev_mapping()))
    for p in bad_names(normalize(names)):
        collector.add(p)
    return collector

def dev_bad_names():
    collector = set([])
    names = chain(object(triple_dev_tree()),subject(triple_dev_tree()))
    for p in bad_names(normalize(names)):
        collector.add(p)
    return collector

def put_in_sesame(graph):
    s = graph.serialize(format="n3")
    con = H.HTTPConnection("107.170.133.175:8080")
    con.request("POST", "/openrdf-sesame/repositories/OpenWorm2/statements", s, {"Content-Type": "application/x-turtle;charset=UTF-8"})
    r = con.getresponse()
    print "sesame response is %d " % r.status

class D:
    namespace = Namespace("http://openworm.org/entities/")
d = D()
def f(i):
    return urlize(normalize_lineage_name(i),d.namespace)

def tree_graph():
    graph = Graph()
    for i in ((f(x[0]), d.namespace[x[1]], f(x[2])) for x in triple_dev_tree()):
        graph.add(i)
    return graph

def adult_dev_graph():
    graph = Graph()
    def j():
        for x in triple_adult_dev_mapping():
            if re.match(goodname_regex,x[2]):
                yield (f(x[2]), RDFS["label"], Literal(str(x[0])))
    for i in j():
        graph.add(i)
    return graph

def upload_tree():
    put_in_sesame(tree_graph())

def upload_adult_dev_mapping():
    put_in_sesame(adult_dev_graph())

def print_serialization(g):
    print g.serialize(format="nt")

if __name__ == "__main__":
    #print_serialization(adult_dev_graph())
    upload_adult_dev_mapping()
    #for x in  dev_bad_names():
        #print x
