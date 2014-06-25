import PyOpenWorm

TestConfig = PyOpenWorm.Configure.open("../tests/test.conf")
config = PyOpenWorm.Data(TestConfig)

worm = PyOpenWorm.Worm(config)

net = worm.get_neuron_network()

types = {}
for neuron in net.neurons():
    try:
        type = net.aneuron(neuron).type()
    except KeyError:
        type = "Unknown"

    if not types.has_key(type):
        types[type] = []
    types[type].append(neuron)
        

for type in types.keys():
    print("Neurons of type %s:\n  %s\n"%(type, types[type]))





