from __future__ import absolute_import
from __future__ import print_function

from owmeta_core.command import OWM
from owmeta_core.dataobject import ObjectProperty
from owmeta_core.custom_dataobject_property import CustomProperty
from owmeta_core.context import Context

from owmeta.neuron import Neuron
from owmeta.network import Network
from owmeta.worm import Worm
from owmeta.evidence import Evidence
from owmeta.document import Document


class NC_neighbor(CustomProperty):
    def __init__(self, *args, **kwargs):
        super(NC_neighbor, self).__init__('_nb', *args, **kwargs)
        self.real_neighbor = self.owner.neighbor

        # Re-assigning neighbor Property
        self.owner.neighbor = self

    def get(self, **kwargs):
        # get the members of the class
        for x in self.owner.neighbor():
            yield x

    def set(self, ob, **kwargs):
        self.real_neighbor(ob)
        if isinstance(ob, NeuronClass):
            ob_name = ob.name()
            this_name = self.owner.name()
            for x in ob.member.defined_values:
                # Get the name for the neighbor

                try:
                    n = x.name()
                    side = n[n.find(ob_name)+len(ob_name):]

                    name_here = this_name + side
                    this_neuron = Neuron(name_here)
                    self.owner.member(this_neuron)
                    this_neuron.neighbor(x, **kwargs)
                except ValueError:
                    # XXX: could default to all-to-all semantics
                    print('Do not recoginze the membership of this neuron/neuron class', ob)
        elif isinstance(ob, Neuron):
            for x in self.owner.member:
                x.neighbor(ob)

    def triples(self, *args, **kwargs):
        """ Stub. All of the actual relationships are encoded in Neuron.neighbor and NeuronClass.member """
        return []


# Circuit from http://www.ncbi.nlm.nih.gov/pmc/articles/PMC2760495/
class NeuronClass(Neuron):
    class_context = 'http://example.org/rmgr_example'

    member = ObjectProperty(value_type=Neuron, multiple=True)

    def __init__(self, name=False, **kwargs):
        super(NeuronClass, self).__init__(**kwargs)
        NC_neighbor(owner=self)
        if name:
            self.name(name)

# A neuron class should be a way for saying what all neurons of a class have in common
# (The notation below is a bit of a mish-mash. basically it's owmeta without
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

def setup(sctx, ctx, name, type):
    n = ctx(NeuronClass)(name)
    n.type(type)
    r = sctx(Neuron).query(name+"R")
    for rs in r.load():
        n.member(rs)
    l = sctx(Neuron).query(name+"L")
    for ls in l.load():
        n.member(ls)
    return n


with OWM('../.owm').connect().transaction() as conn:
    ctx = conn(Context)('http://example.org/data')
    evctx = conn(Context)('http://example.org/evidence')

    w = ctx(Worm)("C. elegans")
    net = ctx(Network)()
    w.neuron_network(net)

    doc = evctx(Document)(title="A Hub-and-Spoke Circuit Drives Pheromone Attraction and Social Behavior in C. elegans",
                          uri="http://www.ncbi.nlm.nih.gov/pmc/articles/PMC2760495/",
                          year=2009)
    ev = evctx(Evidence)(reference=doc)
    ev.supports(ctx.rdf_object)

    sctx = conn(Context)().stored
    rmg = setup(sctx, ctx, "RMG", 'interneuron')
    rmh = setup(sctx, ctx, "RMH", 'motor')
    ask = setup(sctx, ctx, "ASK", 'sensory')
    ash = setup(sctx, ctx, "ASH", 'sensory')
    adl = setup(sctx, ctx, "ADL", 'sensory')
    urx = setup(sctx, ctx, "URX",  'sensory')
    awb = setup(sctx, ctx, "AWB", 'sensory')
    il2 = setup(sctx, ctx, "IL2", 'sensory')

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

    for p, x, o in d:
        if x == 'gj':
            x = 'GapJunction'
        else:
            x = 'Send'
        p.neighbor(o, syntype=x)
    ctx.add_import(Context('http://openworm.org/data'))
    ctx.save()
    ctx.save_imports()
    evctx.save()
    ctx.mapper.add_class(NeuronClass)
    nc = ctx.stored(NeuronClass)()
    nc.type('sensory')

    print('Sensory neuron classes in the circuit and their neurons')
    # XXX: Add an evidence query like ev.asserts(nc.member(P.Neuron("ADLL")))
    for x in nc.load():
        print(x.name(), "has:")
        for y in x.member():
            print(" ", y.name(), "of type", ", ".join(y.type()))
