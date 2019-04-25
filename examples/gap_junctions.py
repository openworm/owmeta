"""
How to get a particular Neuron's gap junctions from the database.
"""

from __future__ import absolute_import
from __future__ import print_function
import PyOpenWorm as P
from PyOpenWorm.worm import Worm
from PyOpenWorm.context import Context

# Connect to existing database.
with P.connect('default.conf') as conn:
    ctx = Context(ident="http://openworm.org/data", conf=conn.conf).stored

    # Put the Worm's Network object in a variable.
    net = ctx(Worm)().get_neuron_network()

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
