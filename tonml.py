import PyOpenWorm

import neuroml
from neuroml import NeuroMLDocument
from neuroml import IafCell
from neuroml import Network
from neuroml import ExpOneSynapse
from neuroml import Population
from neuroml import PulseGenerator
from neuroml import ExplicitInput
from neuroml import SynapticConnection
from PyOpenWorm import Configure
from PyOpenWorm import Data,Configure,Muscle,Network,Neuron,Worm
import neuroml.writers as writers

def s(doc,net,n):
    i = IafCell(id=n.name(),
                       C="1.0 nF",
                       thresh = "-50mV",
                       reset="-65mV",
                       leak_conductance="10 nS",
                       leak_reversal="-65mV")
    pop = Population(id="popOf"+n.name(),component=n.name(),size=1)
    doc.iaf_cells.append(i)
    net.populations.append(pop)

def connect(nml_net,n1,n2,syn_id=False):
    if not syn_id:
        syn_id = n1.name() +":"+ n2.name()
    syn = SynapticConnection(from_="%s[%i]"%("popOf"+n1.name(),0),
            synapse=syn_id,
            to="%s[%i]"%("popOf"+n2.name(),0))
    nml_net.synaptic_connections.append(syn)

###### Validate the NeuroML ######
def v(f):
    from neuroml.utils import validate_neuroml2
    validate_neuroml2(f)

# Takes a neuron object
def main():
    c = Configure()
    c['neuronscsv'] = 'https://raw.github.com/openworm/data-viz/master/HivePlots/neurons.csv'
    c['connectomecsv'] = 'https://raw.github.com/openworm/data-viz/master/HivePlots/connectome.csv'
    c['sqldb'] = '/home/markw/work/openworm/PyOpenWorm/db/celegans.db'
    c = Data(c)
    net = PyOpenWorm.Network(c)
    nml_doc = NeuroMLDocument(id="IafNet")
    ns = net.neurons()

    nml_net = neuroml.Network(id="IafNet")
    nml_doc.networks.append(nml_net)

    for n in [net.aneuron_nocheck(n) for n in ns]:
        s(nml_doc, nml_net, n)

    syn0 = ExpOneSynapse(id="syn0",
            gbase="65nS",
            erev="0mV",
            tau_decay="3ms")
    for k in net.synapses():
        n1 = net.aneuron_nocheck(k[0])
        n2 = net.aneuron_nocheck(k[1])
        connect(nml_net,n1,n2,'syn0')

    f = "test.nml"
    writers.NeuroMLWriter.write(nml_doc, f)
    v(f)


if __name__ == "__main__":
    main()
