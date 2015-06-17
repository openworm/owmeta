import PyOpenWorm as P

P.connect()

class NC_neighbor(P.Property):
    def __init__(self, *args, **kwargs):
        P.Property.__init__(self, '_nb', *args, **kwargs)
        self.real_neighbor = self.owner.neighbor

        # Re-assigning neighbor Property
        self.owner.neighbor = self

    def get(self,**kwargs):
        # get the members of the class
        for x in self.owner.neighbor():
            yield x

    def set(self, ob, **kwargs):
        self.real_neighbor(ob)
        if isinstance(ob, NeuronClass):
            ob_name = ob.name()
            this_name = self.owner.name()
            for x in ob.member():
                # Get the name for the neighbor
                # XXX:

                try:
                    n = x.name()
                    side = n[n.find(ob_name)+len(ob_name):]

                    name_here = this_name + side
                    this_neuron = P.Neuron(name_here)
                    self.owner.member(this_neuron)
                    this_neuron.neighbor(x,**kwargs)
                except ValueError:
                    # XXX: could default to all-to-all semantics
                    print 'Do not recoginze the membership of this neuron/neuron class', ob
        elif isinstance(ob, Neuron):
            for x in self.owner.member:
                x.neighbor(ob)

    def triples(self,*args,**kwargs):
        """ Stub. All of the actual relationships are encoded in Neuron.neighbor and NeuronClass.member """
        return []

# Circuit from http://www.ncbi.nlm.nih.gov/pmc/articles/PMC2760495/
class NeuronClass(P.Neuron):
    def __init__(self, name=False, **kwargs):
        P.Neuron.__init__(self,**kwargs)
        NeuronClass.ObjectProperty('member', owner=self, value_type=P.Neuron, multiple=True)
        NC_neighbor(owner=self)
        if name:
            self.name(name)
NeuronClass.register()

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
    p.neighbor(o, syntype=x)
ev.save()

nc = NeuronClass()
nc.type('sensory')

print 'Sensory neuron classes in the circuit and their neurons'
# XXX: Add an evidence query like ev.asserts(nc.member(P.Neuron("ADLL")))
for x in nc.load():
    print x.name(), "has:"
    for y in x.member():
        print " ", y.name(), "of type", ",".join(y.type())

P.disconnect()
