import owmeta
from time import time
from owmeta.neuron import Neuron
owmeta.connect(configFile='owmeta/default.conf')
t0 = time()

print("Neurons:")
print(", ".join(sorted(Neuron().name.get())))

print("Receptors:")
print(", ".join(sorted(Neuron().receptor.get())))
tot = time() - t0
print ("Took {} seconds".format(tot))
