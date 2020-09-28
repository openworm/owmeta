from __future__ import absolute_import
from __future__ import print_function
import owmeta as P
import datetime
from yarom.quantity import Quantity
from owmeta.channel import Channel
from owmeta.channelworm import PatchClampChannelModel, PatchClampExperiment
from owmeta.context import Context
from owmeta.evidence import Evidence
from owmeta.experiment import Experiment

#Connect to existing database.
P.connect('default.conf')

ctx = Context(ident="http://example.org/bio/ion_channel")

chan = ctx(Channel)(name='Ch0')
chan.subfamily("chanfam")

cm = ctx(PatchClampChannelModel)(key='patch-clamp-01')
cm.ion('K+')
cm.gating('voltage')
chan.model(cm)
pc = ctx(PatchClampExperiment)(key='patch-clamp-01',
                               initial_voltage=Quantity(30, 'mV'),
                               pipette_solution='Ringer\'s solution',
                               start_time=datetime.datetime(2018, 5, 26, 15, 56, 41, 244489),
                               end_time=datetime.datetime(2018, 5, 26, 15, 57, 41, 244489),
                               type='current clamp')

cm.modeled_from(pc)

ctx.save_context()

print(cm.rdf.serialize(format='n3').decode('utf-8'))
chan1 = ctx.stored(Channel)()
print((set(chan1.load())))
