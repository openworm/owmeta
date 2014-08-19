import PyOpenWorm as P
P.connect('PyOpenWorm/default.conf')
P.config()['rdf.graph'].parse('OpenWormData/out.n3', format='n3')
P.disconnect()
