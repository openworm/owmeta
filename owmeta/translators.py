from .data_trans.neuron_data import NeuronCSVDataTranslator
from .data_trans.connections import (NeuronConnectomeCSVTranslator,
                                     NeuronConnectomeSynapseClassTranslator)
from .data_trans.wormatlas import WormAtlasCellListDataTranslator
from .data_trans.wormbase import (WormbaseTextMatchCSVTranslator,
                                  WormbaseIonChannelCSVTranslator,
                                  CellWormBaseCSVTranslator)
from .data_trans.context_merge import ContextMergeDataTranslator


def owm_data(ns):
    ctx = ns.context
    ctx.add_import(NeuronCSVDataTranslator.definition_context)
    ctx.add_import(ContextMergeDataTranslator.definition_context)
    ctx(NeuronConnectomeCSVTranslator)()
    ctx(NeuronConnectomeSynapseClassTranslator)()
    ctx(NeuronCSVDataTranslator)()
    ctx(WormAtlasCellListDataTranslator)()
    ctx(WormbaseIonChannelCSVTranslator)()
    ctx(WormbaseTextMatchCSVTranslator)()
    ctx(ContextMergeDataTranslator)()
    ctx(CellWormBaseCSVTranslator)()
