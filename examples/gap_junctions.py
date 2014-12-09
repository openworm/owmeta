"""
How to get a particular Neuron's gap junctions from the database.
"""

import PyOpenWorm as P

#Connect to existing database.
P.connect('default.conf')

#Put the Worm's Network object in a variable.
net = P.Worm().get_neuron_network()

#Put a particular Neuron object in a variable ('AVAL' in this example).
aval = net.aneuron('AVAL')

#Get the number of gap junctions on that cell.
print aval.GJ_degree()

#Get all Connections to/from AVAL, and only print out the gap junctions.
#We could also put them into an array or do other things with them than print.
for c in net.aneuron('AVAL').connection():
    #the `one()` returns a string like "gapJunction" instead of "syntype=gapJunction"
    if c.syntype.one() == 'gapJunction':
        print c
