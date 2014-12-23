import PyOpenWorm as P

P.connect("default.conf")

worm = P.Worm()

net = worm.get_neuron_network()

types = {}
for neuron in net.neuron():
    if len(list(neuron.type())) > 0:
        type = list(neuron.type())[0]

        if not types.has_key(type):
            types[type] = []

        types[type].append(list(neuron.name())[0])

for type in types.keys():
    print("Neurons of type %s:\n  %s\n"%(type, types[type]))
