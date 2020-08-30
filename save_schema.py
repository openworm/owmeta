from owmeta_core.command import OWM


owm = OWM()

for module in ('owmeta.neuron',
               'owmeta.worm',
               'owmeta.biology',
               'owmeta.cell',
               'owmeta.channel',
               'owmeta.channelworm',
               'owmeta.connection',
               'owmeta.document',
               'owmeta.evidence',
               'owmeta.experiment',
               'owmeta.muscle',
               'owmeta.network',
               'owmeta.plot',
               'owmeta.website',
               'owmeta.data_trans.bibtex',
               'owmeta.data_trans.connections',
               'owmeta.data_trans.context_merge',
               'owmeta.data_trans.data_with_evidence_ds',
               'owmeta.data_trans.neuron_data',
               'owmeta.data_trans.wormatlas',
               'owmeta.data_trans.wormbase',
               'owmeta.sources',
               'owmeta.translators',
               ):
    owm.save(module)
#owm.translate()
