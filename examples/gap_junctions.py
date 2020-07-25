"""
How to get a particular Neuron's gap junctions from the database.
"""

from __future__ import absolute_import
from __future__ import print_function
from owmeta_core.command import OWM
from owmeta_core.context import Context

from owmeta.worm import Worm
from owmeta.neuron import Neuron

# Connect to existing database.
with OWM('../.owm').connect() as conn:
    ctx = Context(ident="http://openworm.org/data", conf=conn.conf).stored

    # Put the Worm's Network object in a variable.
    net = ctx(Worm).query().get_neuron_network()

    # Put a particular Neuron object in a variable ('AVAL' in this example).
    aval = ctx(Neuron).query('AVAL')

    print("Getting all Connections to/from AVAL, and printing the gap junctions")
    # We could also put them into an array or do other things with them other
    # than print.
    num_gjs = 0
    for c in aval.connection():
        # the `one()` returns a string like "gapJunction" instead of
        # "syntype=gapJunction"
        if c.syntype.one() == 'gapJunction':
            num_gjs += 1
            print(num_gjs, c.pre_cell().name(), c.post_cell().name())
