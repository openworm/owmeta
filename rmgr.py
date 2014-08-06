import PyOpenWorm as P

P.connect(conf=P.Data({"rdf.upload_block_statement_count" : 50 }))

# Circuit from http://www.ncbi.nlm.nih.gov/pmc/articles/PMC2760495/
class NeuronClass(P.Neuron):
    def __init__(self, name=False, **kwargs):
        P.Neuron.__init__(self,**kwargs)
        P.ObjectProperty('member', owner=self)
        if name:
            self.name(name)

# A neuron class should be a way for saying what all neurons of a class have in common
# (The notation below is a bit of a mish-mash. basically it's PyOpenWorm without
# iterators, type notations with ':', and some Python string operations)
#
# nc : NeuronClass
# n : Neuron
# p : Property
# a : DataObject
#   | Literal ;
# bc : NeuronClass
# b : Neuron
# d : Neuron
# p.linkName not in {'name', 'connection', 'neighbor'}
# nc.p(a)
#
# bc.member(b)
# b.name(bc.name() + n.name()[-1])
# nc.member(n)
# nc.neighbor(bc)
# nc.neighbor(d)
# class_name = nc.name()
# ------------------------------------[implies]-------
# n.p(a) # Any property except name, connection, and neighbor is the same as in nc
# n.neighbor(d) # For neighbors, if the neighbor is a neuron, then just the connection
#               # holds for all members of the class
# n.neighbor(b) # Otherwise, the neuron (b) in the connected class on the same side as
#               # n (i.e., the one for which the last character in its name matches the
#               # last in n's name) in the neighbor
# n.name()[:-1] == nc.name()

NeuronClass.register()

#
# Setting up the data
#

ev = P.Evidence(title="A Hub-and-Spoke Circuit Drives Pheromone Attraction and Social Behavior in C. elegans",
        uri="http://www.ncbi.nlm.nih.gov/pmc/articles/PMC2760495/",
        year=2009)
w = P.Worm("C. elegans")
net = P.Network()
w.neuron_network(net)
ev.asserts(w)
def setup(name,type):
    n = NeuronClass(name)
    n.type(type)
    n.member(P.Neuron(name+"R"))
    n.member(P.Neuron(name+"L"))
    net.neuron(n)
    return n

rmg = setup("RMG",'interneuron')
rmh = setup("RMH",'motor')
ask = setup("ASK",'sensory')
ash = setup("ASH",'sensory')
adl = setup("ADL",'sensory')
urx = setup("URX",'sensory')
awb = setup("AWB",'sensory')
il2 = setup("IL2",'sensory')

# describing the connections
d = [(ask, 'gj', rmg),
     (rmh, 'gj', rmg),
     (urx, 'gj', rmg),
     (urx, 'sn', rmg),
     (awb, 'gj', rmg),
     (il2, 'gj', rmg),
     (adl, 'gj', rmg),
     (ash, 'sn', rmg),
     (ash, 'gj', rmg),
     (rmg, 'sn', ash)]

for p,x,o in d:
    if x == 'gj':
        x='GapJunction'
    else:
        x='Send'
    p.neighbor(o,syntype=x)
for x in ev.triples():
    print "\t".join(str(z) for z in x)
ev.save()
P.disconnect()
