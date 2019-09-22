"""
Get information about the network.

In this case, we are interested in a small set of neurons. We go through each of
the neurons and get connectivity information about each connection it has with
another cell.

This type of script could be useful for visualizing data, generating reports,
or any number programmatic applications in OpenWorm that involve connectivity.

Try running this script and see what it prints out.
"""
from __future__ import absolute_import
from __future__ import print_function
import owmeta as P
from owmeta.worm import Worm
from owmeta.neuron import Neuron

print("Connecting to the database using owmeta v%s..."%P.__version__)
conn = P.connect('default.conf')

from owmeta.context import Context
ctx = Context(ident="http://openworm.org/data", conf=conn.conf).stored

#Get the worm object.
worm = ctx(Worm)()

#Extract the network object from the worm object.
net = worm.neuron_network()

#Make a list of some arbitrary neuron names.
some_neuron_names = ["ADAL", "AIBL", "I1R", "PVCR", "DD5"]

#Go through our list and get the neuron object associated with each name.
#Store these in another list.
some_neurons = [ctx(Neuron)(name) for name in some_neuron_names]

print("Going through our list of neurons: %s"%some_neuron_names)

for neuron in some_neurons:
    print("Checking connectivity of %s (%s)..." % (neuron.name(), ', '.join(neuron.type())))

    #Go through all synapses in the network.
    #Note that we can go through all connection objects (even gap junctions) by
    #using `net.synapses()` and a for loop, as below.
    conns = {'pre': {"E": [], "I": []}, 'post': {"E": [], "I": []}, 'gap': set()}
    for s in neuron.connection.get('either'):
        print('   - Connection from %s -> %s (%s; %s)'%(s.pre_cell().name(), s.post_cell().name(), s.syntype(), s.synclass()))
        #Below we print different things depending on the connections we find.
        #If the neuron we are currently looking at from our list is the pre or
        #post cell in a connection, we print a different diagram. We also print
        #different letters to symbolize gapJunction connections (G), as well as
        #excitatory (E) and inhibitory (I) neurons.
        type = 'G' if (s.syntype() == "gapJunction") else ('I' if (s.synclass() in ['GABA']) else 'E')
        if s.pre_cell().name() == neuron.name():
            #Note especially how we chain our queries together to get what we
            #want from the database. `s.pre_cell.one()` gives the presynaptic
            #neuron "object" of synapse `s`, so `s.pre_cell.one().name.one()`
            #gives us the name of that presynaptic neuron.
            other = s.post_cell().name()
            if type == 'G':
                conns['gap'].add(other)
            else:
                l = conns['pre'].get(type, [])
                l.append(other)
                conns['pre'][type] = l

        elif s.post_cell().name() == neuron.name():
            other = s.post_cell().name()
            if type == 'G':
                conns['gap'].add(other)
            else:
                l = conns['post'].get(type, [])
                l.append(s.pre_cell().name())
                conns['post'][type] = l

    print("  Excites: "+', '.join(conns["pre"]["E"]))
    print("  Excited by: "+', '.join(conns["post"]["E"]))
    print("  Inhibits: "+', '.join(conns["pre"]["I"]))
    print("  Inhibited by: "+', '.join(conns["post"]["I"]))
    print("  Gap junction neighbors: "+', '.join(conns["gap"]))
    print()

conn.disconnect()
