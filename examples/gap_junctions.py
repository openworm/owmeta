"""
How to get a particular Neuron's gap junctions from the database.
"""

from __future__ import absolute_import
from __future__ import print_function
from PyOpenWorm.worm import Worm
import PyOpenWorm as P

# Connect to existing database.
P.connect('default.conf')


# Put the Worm's Network object in a variable.
net = Worm().get_neuron_network()

# Put a particular Neuron object in a variable ('AVAL' in this example).
aval = net.aneuron('AVAL')

print("Getting all Connections to/from AVAL, and printing the gap junctions")
# We could also put them into an array or do other things with them other
# than print.
num_gjs = 0
for c in aval.connection():
    # the `one()` returns a string like "gapJunction" instead of
    # "syntype=gapJunction"
    if c.syntype.one() == 'gapJunction':
        num_gjs += 1
        print(num_gjs, c)
