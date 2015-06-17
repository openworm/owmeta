from __future__ import print_function
"""
Get information about the network.

In this case, we are interested in a small set of neurons. We go through each of
the neurons and get connectivity information about each connection it has with
another cell.

This type of script could be useful for visualizing data, generating reports,
or any number programmatic applications in OpenWorm that involve connectivity.

Try running this script and see what it prints out. It takes a while to run
because there are so many connections, so feel free to comment out some of the
neuron names in the arbitrary list declared further below.
"""
import PyOpenWorm as P

print("Connecting to the database...")
P.connect()

#Get the worm object.
worm = P.Worm()

#Extract the network object from the worm object.
net = worm.neuron_network()

#Make a list of some arbitrary neuron names.
some_neuron_names = ["ADAL", "AIBL", "I1R", "PVCR"]

#Go through our list and get the neuron object associated with each name.
#Store these in another list.
some_neurons = [P.Neuron(name) for name in some_neuron_names]

print("Going through our list of neurons:")
for neuron in some_neurons:
    print("Checking connectivity of %s"%neuron.name())

    #Go through all synapses in the network.
    #Note that we can go through all connection objects (even gap junctions) by
    #using `net.synapses()` and a for loop, as below.
    conns = {'pre':{"E":[], "I":[]}, 'post':{"E":[], "I":[]}, 'gap':set()}
    for s in neuron.connection.get('either'):
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
    print("Excites")
    print(conns["pre"]["E"])
    print("Excited by")
    print(conns["post"]["E"])
    print("Inhibits")
    print(conns["pre"]["I"])
    print("Inhibited by")
    print(conns["post"]["I"])
    print("Gap junction neighbors")
    print(conns["gap"])
