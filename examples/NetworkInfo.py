import PyOpenWorm

TestConfig = PyOpenWorm.Configure.open("../tests/test.conf")
config = PyOpenWorm.Data(TestConfig)

worm = PyOpenWorm.Worm(config)

net = worm.get_neuron_network()

some_neuron_names = ["ADAL", "AIBL", "I1L", "I1R", "PVCR", "DB5"]
some_neurons = [net.aneuron(name) for name in some_neuron_names]

for neuron in some_neurons:
    print("Checking connectivity of %s"%neuron.name())
    
    for s in net.synapses():
        type = 'G' if (s.syntype == "GapJunction") else ('I' if s.synclass in ['GABA'] else 'E') 
        
        if s.pre_cell == neuron.name():
            print("o-> %s %s"%(type, s))
        elif s.post_cell == neuron.name():
            print("->o %s %s"%(type, s))








