import PyOpenWorm as P
P.Configureable.default = P.Data.open("tests/test.conf")
P.Configureable.default.openDatabase()
try:
    #tests = [P.Neuron(),P.Neuron(lineageName="AB"),P.Neuron(name="ADAL"),P.Connection(),P.Connection(pre_cell="ADAL",post_cell="PVCR",syntype='send',synclass='Acetycholine')]
    #tests[len(tests)-1].save()
    #for x in tests[len(tests)-2].load():
        #print x
    P.Connection(pre_cell='PVCL', post_cell='AVAL').save()
    P.Connection(pre_cell='AVAL', post_cell='PVCR', number=30).save()
    P.Connection(pre_cell='AVAL', post_cell='PVCR', number=10).save()
    P.Connection(pre_cell='AVAL', post_cell='LOLR', number=30).save()
    query_object = P.Connection(pre_cell='AVAL')
    print 'STARTING WITH AVAL'
    for x in query_object.load():
        cc = x
    print
    print 'STARTING WITH PVCL'
    query_object = P.Connection(pre_cell='PVCL')
    for x in query_object.load():
        print x

    print
    print 'NEURONS'
    query_object = P.Neuron()
    for x in query_object.load():
        print x
    print
    print 'NEIGHBORS of PVCL'
    query_object = P.Neuron(name='PVCL')
    for x in query_object.neighbor():
        print x
    print
    print 'NEIGHBORS of AVAL with number=30 connections'
    query_object = P.Neuron(name='AVAL')
    for x in query_object.neighbor():
        print x
finally:
    P.Configureable.default.closeDatabase()
