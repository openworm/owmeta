import sys
import PyOpenWorm as P
if len(sys.argv) > 1:
    dest = sys.argv[1]
else:
    dest = '../WormData.n3'

P.connect('default.conf')
# XXX: Properties aren't initialized until the first object of a class is created,
#      so we create them here

for x in dir(P):
    if isinstance(getattr(P, x), type) and issubclass(getattr(P, x), P.DataObject):
        c = getattr(P, x)
        if x == 'values':
            c("dummy")
        else:
            c()
P.config('rdf.graph').serialize(dest, format='n3')
