import PyOpenWorm as P
P.connect()
aval = P.Cell(name="AVAL")
morph = aval.morphology()
print morph
P.disconnect()
