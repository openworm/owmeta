import sys
import PyOpenWorm as P

P.connect("default.conf")

worm = P.Worm()

net = worm.get_neuron_network()

some_neuron_names = ["ADAL"] #, "AIBL", "I1L", "I1R", "PVCR", "DB5"
some_neurons = [P.Neuron(name) for name in some_neuron_names]

for neuron in some_neurons:
    print("Checking connectivity of %s"%neuron.name.one())

    for s in net.synapses():
        type = 'G' if (s.syntype.one() == "gapJunction") else ('I' if (s.synclass.one() in ['GABA']) else 'E')
        print type
        print s.pre_cell.one()
        if s.pre_cell.one() == neuron.name.one():
            print("o-> %s %s"%(type, s))
        elif s.post_cell.one() == neuron.name.one():
            print("->o %s %s"%(type, s))
