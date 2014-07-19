import sys
sys.path.insert(0,'..')

import PyOpenWorm as P

P.connect(configFile="readme.conf")

g = P.Configureable.default['rdf.graph']
t = P.Neuron().rdf_type


worm = P.Worm()
for x in worm.load():
    print x

net = worm.get_neuron_network()

types = {}
for neuron in net.neuron():
    try:
        type = next(neuron.type())
    except KeyError:
        type = "Unknown"

    if not types.has_key(type):
        types[type] = []
    types[type].append(next(neuron.name()))


for type in types.keys():
    print("Neurons of type %s:\n  %s\n"%(type, types[type]))





