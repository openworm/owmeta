import PyOpenWorm
from time import time
PyOpenWorm.connect('PyOpenWorm/default.conf')
t0 = time()

print("Neurons:")
print(", ".join(sorted(PyOpenWorm.Neuron().name.get())))

print("Receptors:")
print(", ".join(sorted(PyOpenWorm.Neuron().receptor.get())))
tot = time() - t0
print ("Took {} seconds".format(tot))
