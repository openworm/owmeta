from .data_trans.neuron_data import NeuronCSVDataTranslator
from .data_trans.connections import (NeuronConnectomeCSVTranslator,
                                     NeuronConnectomeSynapseClassTranslator)
from .data_trans.wormatlas import WormAtlasCellListDataTranslator
from .data_trans.wormbase import (WormbaseTextMatchCSVTranslator,
                                  MuscleWormBaseCSVTranslator,
                                  NeuronWormBaseCSVTranslator,
                                  WormbaseIDSetter,
                                  WormbaseIonChannelCSVTranslator)
from .data_trans.context_merge import ContextMergeDataTranslator


def owm_data(ns):
    ctx = ns.context
    ctx.add_import(NeuronCSVDataTranslator.definition_context)
    ctx.add_import(ContextMergeDataTranslator.definition_context)
    ctx(MuscleWormBaseCSVTranslator)()
    ctx(NeuronConnectomeCSVTranslator)()
    ctx(NeuronConnectomeSynapseClassTranslator)()
    ctx(NeuronCSVDataTranslator)()
    ctx(NeuronWormBaseCSVTranslator)()
    ctx(WormAtlasCellListDataTranslator)()
    ctx(WormbaseIDSetter)()
    ctx(WormbaseIonChannelCSVTranslator)()
    ctx(WormbaseTextMatchCSVTranslator)()
    ctx(ContextMergeDataTranslator)()
