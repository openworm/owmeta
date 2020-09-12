from owmeta_core.bundle import Bundle
from owmeta_core.context import Context
from owmeta.neuron import Neuron
from owmeta.worm import Worm


with Bundle('openworm/owmeta-data') as bnd:
    ctx = bnd(Context)(ident="http://openworm.org/data").stored
    # Extract the network object from the worm object.
    net = ctx(Worm).query().neuron_network()

    syn = net.synapse.expr
    pre = syn.pre_cell
    post = syn.post_cell

    (pre | post).rdf_type(multiple=True)

    (pre | post).name()
    pre()
    post()
    syn.syntype()
    syn.synclass()
    syn.number()
    connlist = syn.to_objects()

conns = []
for conn in connlist:
    if (Neuron.rdf_type in conn.pre_cell.rdf_type and
            Neuron.rdf_type in conn.post_cell.rdf_type):
        num = conn.number
        syntype = conn.syntype or ''
        synclass = conn.synclass or ''
        pre_name = conn.pre_cell.name
        post_name = conn.post_cell.name

        print(' '.join((pre_name, post_name, str(num), syntype, synclass)))
