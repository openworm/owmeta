import PyOpenWorm as P
P.connect('default.conf')
P.config()['rdf.graph'].serialize('../WormData.n3', format='n3')
