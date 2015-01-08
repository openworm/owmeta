import PyOpenWorm as P
P.connect('default.conf')
P.config()['rdf.graph'].serialize('../out.n3', format='n3')
