import sys
sys.path.insert(0,'..')

import PyOpenWorm as P

P.connect(configFile="readme.conf", do_logging=False)
try:

    query_object = P.Connection(pre_cell='AVAL')
    print 'STARTING WITH AVAL'
    for x in query_object.load():
        print x
    print
    print 'STARTING WITH PVCL'
    query_object = P.Connection(pre_cell='PVCL')
    for x in query_object.load():
        print x

    print
    print 'NEURONS'
    query_object = P.Neuron()
    # sometimes a neuron object with the same name is returned more than once
    names = dict()
    for x in query_object.load():
         n = next(x.name())
         if n not in names:
             names[n] = dict()
             print n
    print
    print 'NEIGHBORS of PVCL'
    query_object = P.Neuron(name='PVCL')
    for x in query_object.neighbor():
        print next(x.name())
    print
    print 'NEIGHBORS of AVAL with number=3 connections'
    query_object = P.Neuron(name='AVAL')
    for x in query_object.neighbor.get(number=3):
        print next(x.name())
    print
    print 'NEURONS and their RECEPTORS'
    for x in names:
        # Wrap in a try-block in case there are no receptors listed
        print x,
        try:
            for r in P.Neuron(name=x).receptor():
                print ' ', r,
        except StopIteration:
            pass
        print
    print
    print 'FIRST 100 OBJECTS'
    for x in zip(P.DataObject().load(), range(100)):
        print x[0]
finally:
    P.disconnect()
