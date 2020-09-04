from owmeta_core.command import OWM
from owmeta.data_trans.wormbase import (MuscleWormBaseCSVTranslator, WormBaseCSVDataSource,
                                        WormbaseIonChannelCSVDataSource, WormbaseIonChannelCSVTranslator,
                                        NeuronWormBaseCSVTranslator, WormbaseTextMatchCSVTranslator,
                                        WormbaseTextMatchCSVDataSource)
from owmeta.data_trans.neuron_data import NeuronCSVDataSource, NeuronCSVDataTranslator
from owmeta.data_trans.connections import (NeuronConnectomeCSVTranslator,
                                           ConnectomeCSVDataSource,
                                           NeuronConnectomeSynapseClassTranslator)
from owmeta.data_trans.context_merge import ContextMergeDataTranslator


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

# We don't have to use the URIs for sources here since we're recreating the
ctx = owm.default_context.stored
muscles = owm.translate(MuscleWormBaseCSVTranslator(),
        data_sources=[WormBaseCSVDataSource(key='wormbase_celegans_cells')],
        output_key='muscles')
ctx(muscles).description(
        "Contains descriptions of C. elegans muscles and is the"
        " principle such list for OpenWorm")

neurons = owm.translate(NeuronCSVDataTranslator(),
        data_sources=[NeuronCSVDataSource(key='neurons')],
        output_key='neurons')
ctx(neurons).description(
        "Contains descriptions of C. elegans neurons and is the"
        " principle such list for OpenWorm")

ion_channels = owm.translate(
        WormbaseIonChannelCSVTranslator(),
        data_sources=[WormbaseIonChannelCSVDataSource(key='ion_channels')],
        output_key='ion_channels')
ctx(ion_channels).description(
        "Contains Channels and ExpressionPatterns")

wb_neurons = owm.translate(
        NeuronWormBaseCSVTranslator(),
        data_sources=[WormBaseCSVDataSource(key='wormbase_celegans_cells')],
        output_key='wormbase_neurons')
ctx(wb_neurons).description(
        'Contains neurons and links to C. elegans. Partially redundant to the Worm Atlas'
        ' data source')

bently_expression = owm.translate(
        NeuronCSVDataTranslator(),
        data_sources=[NeuronCSVDataSource(key='bently_expression')],
        output_key='bently_expression')
ctx(bently_expression).description(
        'Adds receptor, neurotransmitter, and neuropeptide relationships for Neurons')

muscle_ion_channels = owm.translate(
        WormbaseTextMatchCSVTranslator(),
        data_sources=[WormbaseTextMatchCSVDataSource(key='muscle_ion_channels')],
        output_key='muscle_ion_channels')
ctx(muscle_ion_channels).description(
        'Adds relationships between muscles and ion channels')

neuron_ion_channels = owm.translate(
        WormbaseTextMatchCSVTranslator(),
        data_sources=[WormbaseTextMatchCSVDataSource(key='neuron_ion_channels')],
        output_key='neuron_ion_channels')
ctx(neuron_ion_channels).description(
        'Adds relationships between neurons and ion channels')

emmons_connectome = owm.translate(
        NeuronConnectomeCSVTranslator(),
        data_sources=[ConnectomeCSVDataSource(key='emmons')],
        named_data_sources=dict(muscles_source=muscles, neurons_source=neurons),
        output_key='connectome')
ctx(emmons_connectome).description(
        'C. elegans connectome')

connectome_synclass = owm.translate(
        NeuronConnectomeSynapseClassTranslator(),
        data_sources=[emmons_connectome],
        named_data_sources=dict(
            neurotransmitter_source=ConnectomeCSVDataSource(key='connectome')),
        output_key='synclass')

combined_data_source = owm.translate(
        ContextMergeDataTranslator(),
        data_sources=[
            muscles,
            neurons,
            ion_channels,
            wb_neurons,
            bently_expression,
            muscle_ion_channels,
            neuron_ion_channels,
            emmons_connectome],
        output_identifier='http://openworm.org/data')

ctx.save()
