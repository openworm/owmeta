#!/usr/bin/env python
"""
This file is used as a module in shortest_path.py
"""

import re
import sys
#import random as rnd
import numpy as np
import fileinput
def lca_table_print_matrix(M,labels,item_width=1):
    for i in labels:
        for j in labels:
            if M.has_key((i, j)):
                print "%*s" % (item_width,repr(M[(str(i), str(j))])),
            else:
                print "%*s" % (item_width,"."),
        print

def tree_from_file(file_name):
    M = None
    # Note, zip makes a list sized to the smaller sequence
    i = 0
    for line in fileinput.input(file_name):
        vs = re.split(' +', line)
        if i == 0:
            numverts = len(vs)
            M = np.zeros( (numverts + 1, numverts) )
        for (v,j) in zip(vs,range(0,numverts)):
            try:
                k = float(v)
            except:
                k = float('+inf')
            if i == j:
                k = 0
            M[i,j] = k
        i += 1
    return M

def apsp(M):
    nv = M.shape[1]
    for level in range(1,nv+1):
        for i in range(0,nv):
            for j in range(0,nv):
                level_i = min(nv-1,level) # min(4,level) # why the hell is this 4??
                if (M[i, level_i] + M[level_i, j] < M[i,j]):
                    M[i,j] = M[i, level_i] + M[level_i, j]

if __name__ == '__main__':
    M = tree_from_file(sys.argv[1])
    apsp(M)
    numverts=M.shape[1]
    for i in range(0,numverts):
        for j in range(0,numverts):
            print str(int(M[i,j])) + " ",
        print
