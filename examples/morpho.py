import PyOpenWorm as P
d = P.Data.open('../tests/test.conf')
d['rdf.store_conf'] = ("http://107.170.133.175:8080/openrdf-sesame/repositories/OpenWorm2","http://107.170.133.175:8080/openrdf-sesame/repositories/OpenWorm2/statements")
P.connect(conf=d)
aval = P.Cell(name="AVAL")
morph = aval.morphology()
print morph
