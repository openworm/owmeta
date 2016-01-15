"""
Get the length of the shortest path between any two neurons.
Takes connection strength into account by taking the inverse of the number as the weight between edges.

Generates some files to be used with numpy.
"""
from __future__ import absolute_import

import sys
import six
sys.path.insert(0,'..')

import apsp
import PyOpenWorm as P
import numpy as np
# Start PyOpenWorm
P.connect()
try:
    # make the matrix
    try:
        # Try to load from a previous run -- the worm isn't changing
        mat = np.load("celegans.npy")
    except:
        # Get a dictionary of cell names to generated indices used to index into the matrix below
        cell_names = { x[1] : x[0] for x in enumerate({ str(x.name()) for x in P.Neuron().load() }) }
        # Load all of the connections between neurons
        conns = P.Connection().load()

        # initialize matrix entries to +infinity = no direct connection
        inf = float('+inf')
        mat = np.zeros( (len(cell_names) + 1, len(cell_names)) )
        mat.fill(inf)
        for x in conns:
            pre_cell = x.pre_cell()
            post_cell = x.post_cell()
            if isinstance(pre_cell, P.Neuron) \
                    and isinstance(post_cell, P.Neuron):
                pre_name = pre_cell.name()
                post_name = post_cell.name()
                num = x.number()
                if num is None:
                    num = 1.0

                mat[cell_names[pre_name], cell_names[post_name]] = 1.0 / num
                mat[cell_names[post_name], cell_names[pre_name]] = 1.0 / num

        for c in cell_names:
            mat[cell_names[c], cell_names[c]] = 0
        # save the connections matrix
        np.save("celegans.npy", mat)

        # save the cell indices
        f = open("cell_indices",'w')
        for key, value in sorted(six.iteritems(cell_names), key=lambda k_v: k_v[1]):
            f.write("%s: %s\n" % (key, value))
        f.close()

    # Run floyd-warshall all pairs shortest path on the connections matrix
    apsp.apsp(mat)
    # and save it
    np.save("celegans_apsp.npy", mat)

finally:
    # Be sure to disconnect from PyOpenWorm to prevent resource leaks!
    P.disconnect()
