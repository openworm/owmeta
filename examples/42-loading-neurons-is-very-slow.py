import PyOpenWorm
from time import time
from PyOpenWorm.neuron import Neuron
PyOpenWorm.connect(configFile='PyOpenWorm/default.conf')
t0 = time()

print("Neurons:")
print(", ".join(sorted(Neuron().name.get())))

print("Receptors:")
print(", ".join(sorted(Neuron().receptor.get())))
tot = time() - t0
print ("Took {} seconds".format(tot))
