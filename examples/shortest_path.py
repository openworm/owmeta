# Get the shortest path between any two neurons
import apsp
import PyOpenWorm as P
import numpy as np
# Start PyOpenWorm
P.connect(configFile='readme.conf')
try:
    # make the matrix
    try:
        # Try to load from a previous run -- the worm isn't changing
        mat = load("celegans.npy")
    except:
        # Get a dictionary of cell names to generated indices used to index into the matrix below
        cell_names = { x[1] : x[0] for x in enumerate(set(str(next(x.name())) for x in P.Neuron().load())) }
        # Load all of the connections between neurons
        conns = P.Connection().load()

        # initialize matrix entries to +infinity = no direct connection
        inf = float('+inf')
        mat = np.zeros( (len(cell_names) + 1, len(cell_names)) )
        mat.fill(inf)
        for x in conns:
            pre_cell = next(x.pre_cell())
            post_cell = next(x.post_cell())
            pre_name = next(pre_cell.name())
            post_name = next(post_cell.name())
            mat[cell_names[pre_name], cell_names[post_name]] = 1
            mat[cell_names[post_name], cell_names[pre_name]] = 1

        for c in cell_names:
            mat[cell_names[c], cell_names[c]] = 0
        # save the connections matrix
        np.save("celegans.npy", mat)

        # save the cell indices
        f = file("cell_indices",'w')
        for key, value in sorted(cell_names.iteritems(), key=lambda (k,v): v):
            f.write("%s: %s\n" % (key, value))
        f.close()

    # Run floyd-warshall all pairs shortest path on the connections matrix
    apsp.apsp(mat)
    # and save it
    np.save("celegans_apsp.npy", mat)

finally:
    # Be sure to disconnect from PyOpenWorm to prevent resources leaks!
    P.disconnect()

