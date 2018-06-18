from __future__ import print_function
from warnings import warn
from time import time
import PyOpenWorm as P
from PyOpenWorm.context import Context
import traceback
import csv
import os
from yarom import MAPPER
from PyOpenWorm.data_trans.neuron_data import (NeuronCSVDataSource,
                                               NeuronCSVDataTranslator)

from PyOpenWorm.package_utils import get_library_location

import PyOpenWorm.import_override as impo
impo.Overrider(MAPPER).wrap_import()

from PyOpenWorm.data_trans.data_with_evidence_ds import DataWithEvidenceDataSource
from PyOpenWorm.data_trans.wormbase import (WormbaseTextMatchCSVTranslator,
                                            WormBaseCSVDataSource,
                                            WormbaseTextMatchCSVDataSource,
                                            MuscleWormBaseCSVTranslator,
                                            NeuronWormBaseCSVTranslator,
                                            WormbaseIonChannelCSVTranslator,
                                            WormbaseIonChannelCSVDataSource)

from PyOpenWorm.data_trans.wormatlas import (WormAtlasCellListDataSource,
                                             WormAtlasCellListDataTranslator)

from PyOpenWorm.data_trans.connections import (ConnectomeCSVDataSource,
                                               NeuronConnectomeCSVTranslator)

from PyOpenWorm.channel import Channel
from PyOpenWorm.neuron import Neuron
from PyOpenWorm.muscle import Muscle

LINEAGE_LIST_LOC = 'C. elegans Cell List - WormAtlas.tsv'
WORM = None
OPTIONS = None
CELL_NAMES_SOURCE = "C. elegans Cell List - WormBase.csv"
CONNECTOME_SOURCE = "herm_full_edgelist.csv"
IONCHANNEL_SOURCE = "ion_channel.csv"
CHANNEL_MUSCLE_SOURCE = "Ion channels - Ion Channel To Body Muscle.tsv"
CHANNEL_NEURON_SOURCE = "Ion channels - Ion Channel To Neuron.tsv"
CHANNEL_NEUROMLFILE = "NeuroML_Channel.csv"
NEURON_EXPRESSION_DATA_SOURCE = "Modified celegans db dump.csv"

ADDITIONAL_EXPR_DATA_DIR = 'expression_data'


def aux_data():
    d = get_library_location('OpenWormData')
    return os.path.join(d, 'aux_data')


# TODO: Make PersonDataTranslators and Document/Website DataSource for the
# documents these come from. Need to verify who made the translation from the
# website / document
def init_sources():
    return [
        WormbaseTextMatchCSVDataSource(
            key='WormbaseTextMatchCSVChannelNeuronDataSource',
            cell_type=Neuron,
            csv_file_name=CHANNEL_NEURON_SOURCE,
            initial_cell_column=101),
        WormbaseTextMatchCSVDataSource(
            key='WormbaseTextMatchCSVChannelMuscleDataSource',
            cell_type=Muscle,
            csv_file_name=CHANNEL_MUSCLE_SOURCE,
            initial_cell_column=6),
        WormbaseIonChannelCSVDataSource(
            key='WormbaseIonChannelCSVDataSource',
            csv_file_name=IONCHANNEL_SOURCE),
        NeuronCSVDataSource(
            key='WormAtlasNeuronTypesSource',
            csv_file_name=NEURON_EXPRESSION_DATA_SOURCE,
            bibtex_files=['bibtex_files/altun2009.bib',
                          'bibtex_files/WormAtlas.bib']),
        WormBaseCSVDataSource(
            key='WormBaseCSVDataSource',
            csv_file_name=CELL_NAMES_SOURCE,
            description="CSV converted from this Google Spreadsheet: "
                        "https://docs.google.com/spreadsheets/d/"
                        "1NDx9LRF_B2phR5w4HlEtxJzxx1ZIPT2gA0ZmNmozjos/edit#gid=1"),
        WormAtlasCellListDataSource(
            key='WormAtlasCellList',
            csv_file_name=LINEAGE_LIST_LOC,
            description="CSV converted from this Google Spreadsheet: "
                        "https://docs.google.com/spreadsheets/d/"
                        "1Jc9pOJAce8DdcgkTgkUXafhsBQdrer2Y47zrHsxlqWg/edit"),
        ConnectomeCSVDataSource(
            key='EmmonsConnectomeCSVDataSource',
            csv_file_name=CONNECTOME_SOURCE)
    ]


def init_extra_sources(basedir):
    res = []
    for root, _, filenames in os.walk(os.path.join(basedir, ADDITIONAL_EXPR_DATA_DIR)):
        for filename in sorted(filenames):
            if filename.lower().endswith('.csv'):
                name = 'NeuronCSVExpressionDataSource_' + os.path.basename(filename).rsplit('.', 1)[0]
                relpath = os.path.relpath(os.path.join(root, filename), basedir)
                res.append(NeuronCSVDataSource(csv_file_name=relpath, key=name))

    return res


def init_translators():
    return [
        ('WormbaseTextMatchCSVChannelNeuronDataSource',
         WormbaseTextMatchCSVTranslator),
        (('WormAtlasCellList', 'Neurons'),
         WormAtlasCellListDataTranslator),
        ('WormbaseTextMatchCSVChannelMuscleDataSource',
         WormbaseTextMatchCSVTranslator),
        ('WormbaseIonChannelCSVDataSource',
         WormbaseIonChannelCSVTranslator),
        ('WormAtlasNeuronTypesSource',
         NeuronCSVDataTranslator,
         'Neurons'),
        ('WormBaseCSVDataSource',
         MuscleWormBaseCSVTranslator,
         'Muscles'),
        (('EmmonsConnectomeCSVDataSource', 'Neurons', 'Muscles'),
         NeuronConnectomeCSVTranslator),
        ('WormBaseCSVDataSource',
         NeuronWormBaseCSVTranslator)
    ]


def init_extra_neuron_data_translators(sources):
    res = []
    for s in sources:
        res.append((s.key, NeuronCSVDataTranslator))
    return res


def serialize_as_nquads():
    P.config('rdf.graph').serialize('WormData.n4', format='nquads')
    print('serialized to nquads file')


def attach_neuromlfiles_to_channel():
    """ attach the links to the neuroml files for the ion channels
    """
    print("attaching links to neuroml files")
    try:
        with open(CHANNEL_NEUROMLFILE) as csvfile:
            next(csvfile, None)
            csvreader = csv.reader(csvfile, skipinitialspace=True)
            for row in csvreader:
                ch = Channel(name=str(row[0]))
                ch.neuroML_file(str(row[1]))
                ch.save()
        print("neuroML file links attached")
    except Exception:
        traceback.print_exc()


def infer():
    from rdflib import Graph
    from FuXi.Rete.RuleStore import SetupRuleStore
    from FuXi.Rete.Util import generateTokenSet
    from FuXi.Horn.HornRules import HornFromN3

    try:
        w = WORM
        semnet = w.rdf  # fetches the entire worm.db graph

        rule_store, rule_graph, network = SetupRuleStore(makeNetwork=True)
        closureDeltaGraph = Graph()
        network.inferredFacts = closureDeltaGraph

        #build a network of rules
        for rule in HornFromN3('inference_rules.n3'):
            network.buildNetworkFromClause(rule)

        network.feedFactsToAdd(generateTokenSet(semnet)) # apply rules to original facts to infer new facts

        # combine original facts with inferred facts
        for x in closureDeltaGraph:
            w.rdf.add(x)

        ## uncomment next 4 lines to print inferred facts to human-readable file (demo purposes)
        # inferred_facts = closureDeltaGraph.serialize(format='n3') #format inferred facts to notation 3
        # inferred = open('what_was_inferred.n3', 'w')
        # inferred.write(inferred_facts)
        # inferred.close()

    except Exception:
        traceback.print_exc()
    print ("filled in with inferred data")


def do_insert(ident, config="default.conf", logging=False, imports_context_ident=None, basedir=aux_data()):

    sources = init_sources()
    extras = init_extra_sources(basedir)
    data_sources_by_key = {x.key: x for x in sources + extras}
    trans_map = init_translators() + init_extra_neuron_data_translators(extras)
    P.connect(configFile=config, do_logging=logging)
    P.config()

    CTX = Context(ident=ident + '-data', imported=(P.CONTEXT,), conf=P.config())

    EVCTX = Context(ident=ident + '-evidence', imported=(P.CONTEXT,), conf=P.config())

    IWCTX = Context(ident=ident, imported=(CTX, EVCTX), conf=P.config())

    imports_context = Context(ident=imports_context_ident, conf=P.config())

    try:
        t0 = time()
        translators = dict()
        remaining = list(trans_map)
        last_remaining = None
        saved_contexts = set([])
        while remaining != last_remaining:
            next_remaining = []
            for t in remaining:
                if not isinstance(t[0], (list, tuple)):
                    source_keys = (t[0],)
                else:
                    source_keys = t[0]

                sources = tuple(data_sources_by_key.get(s) for s in source_keys)
                if None in sources:
                    next_remaining.append(t)
                    continue
                translator_class = t[1]
                if len(t) > 2:
                    output_key = t[2]
                else:
                    output_key = None
                translator = translators.get(translator_class, None)
                if not translator:
                    translator = translator_class()
                    translators[translator_class] = translator

                print('\n'.join('Input({}/{}): {}'.format(i + 1, len(sources), s) for i, s in enumerate(sources)))
                print('Translating with {}'.format(translator))
                orig_wd = os.getcwd()
                os.chdir(basedir)
                try:
                    res = translator(*sources, output_key=output_key)
                finally:
                    os.chdir(orig_wd)

                print('Result: {}'.format(res))
                if isinstance(res, DataWithEvidenceDataSource):
                    res.data_context.save_context(inline_imports=True, saved_contexts=saved_contexts)
                    res.data_context.save_imports(imports_context)
                    res.evidence_context.save_context(inline_imports=True, saved_contexts=saved_contexts)
                    res.evidence_context.save_imports(imports_context)
                    for ctx in res.contexts:
                        raise Exception()

                if res:
                    if res.key:
                        data_sources_by_key[res.key] = res
                    else:
                        data_sources_by_key[res.identifier] = res
            last_remaining = list(remaining)
            remaining = next_remaining
        for x in remaining:
            warn("Failed to process: {}".format(x))

        # attach_neuromlfiles_to_channel()

        t1 = time()
        print("Saving data...")
        graph = P.config('rdf.graph')
        for src in data_sources_by_key.values():
            if isinstance(src, DataWithEvidenceDataSource):
                print('saving', src)
                CTX.add_import(src.data_context)
                EVCTX.add_import(src.evidence_context)
                for ctx in src.contexts:
                    IWCTX.add_import(ctx)
        IWCTX.save_context(graph, saved_contexts=saved_contexts)
        IWCTX.save_imports(imports_context)
        print('imports context size', len(imports_context))
        print("Saved %d triples." % IWCTX.triples_saved)
        t2 = time()

        print("Serializing...")
        serialize_as_nquads()
        t3 = time()
        print("generating objects took", t1 - t0, "seconds")
        print("saving objects took", t2 - t1, "seconds")
        print("serializing objects took", t3 - t2, "seconds")

    except Exception:
        traceback.print_exc()
    finally:
        P.disconnect()


if __name__ == '__main__':
    # NOTE: This process will NOT clear out the database if run multiple times.
    #       Multiple runs will add the data again and again.
    # Takes about 5 minutes with ZODB FileStorage store
    # Takes about 3 minutes with Sleepycat store

    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-l", "--do-logging", dest="do_logging",
                      action="store_true", default=False,
                      help="Enable log output")
    parser.add_option("-c", "--config", dest="config", default='default.conf',
                      help="Config file")

    (options, _) = parser.parse_args()
    OPTIONS = options

    do_insert("http://openworm.org/entities/bio#worm0", config=options.config, logging=options.do_logging)
