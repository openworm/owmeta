from __future__ import print_function
from warnings import warn
from time import time
from rdflib.namespace import Namespace
import PyOpenWorm as P
from PyOpenWorm.context import Context
from PyOpenWorm.bibtex import parse_bibtex_into_documents
import traceback
import csv
import os
from yarom import MAPPER
from PyOpenWorm.data_trans.common_data import TRANS_NS, DS_NS

import PyOpenWorm.import_override as impo
impo.Overrider(MAPPER).wrap_import()
CTX = Context(ident="http://openworm.org/entities/bio#worm0-data",
              imported=(P.CONTEXT,))

from PyOpenWorm.data_trans.csv_ds import CSVDataSource
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

from CTX.PyOpenWorm.channel import Channel
from CTX.PyOpenWorm.neuron import Neuron
from CTX.PyOpenWorm.muscle import Muscle

EVCTX = Context(ident="http://openworm.org/entities/bio#worm0-evidence",
                imported=(P.CONTEXT,))

from EVCTX.PyOpenWorm.evidence import Evidence
from EVCTX.PyOpenWorm.document import Document
from EVCTX.PyOpenWorm.datasource import (DataTranslator,
                                         Informational)

IWCTX = Context(ident="http://openworm.org/entities/bio#worm0",
                imported=(CTX, EVCTX))

LINEAGE_LIST_LOC = '../aux_data/C. elegans Cell List - WormAtlas.tsv'
WORM = None
OPTIONS = None
CELL_NAMES_SOURCE = "../aux_data/C. elegans Cell List - WormBase.csv"
CONNECTOME_SOURCE = "../aux_data/herm_full_edgelist.csv"
IONCHANNEL_SOURCE = "../aux_data/ion_channel.csv"
CHANNEL_MUSCLE_SOURCE = "../aux_data/Ion channels - Ion Channel To Body Muscle.tsv"
CHANNEL_NEURON_SOURCE = "../aux_data/Ion channels - Ion Channel To Neuron.tsv"
CHANNEL_NEUROMLFILE = "../aux_data/NeuroML_Channel.csv"
NEURON_EXPRESSION_DATA_SOURCE = "../aux_data/Modified celegans db dump.csv"

ADDITIONAL_EXPR_DATA_DIR = '../aux_data/expression_data'


class NeuronCSVDataSource(CSVDataSource):
    rdf_namespace = Namespace(DS_NS['NeuronCSVDataSource#'])
    bibtex_files = Informational(display_name='BibTeX files',
                                 description='List of BibTeX files that are referenced in the csv file by entry ID')


class NeuronCSVDataTranslator(DataTranslator):
    input_type = NeuronCSVDataSource
    output_type = DataWithEvidenceDataSource
    translator_identifier = TRANS_NS.NeuronCSVDataTranslator

    def __init__(self, *args, **kwargs):
        super(NeuronCSVDataTranslator, self).__init__(*args, **kwargs)
        self.__document_contexts = dict()

    def translate(self, data_source):
        res = self.make_new_output((data_source,))

        documents = dict()
        bibtex_files = data_source.bibtex_files.onedef()
        if bibtex_files is not None:
            for bib in bibtex_files:
                documents.update(parse_bibtex_into_documents(bib, res.evidence_context))

        with open(data_source.csv_file_name.onedef()) as f:
            reader = csv.reader(f)
            next(reader)  # skip the header row

            for row in reader:
                neuron_name, relation, data, evidence, documentURL = row
                relation = relation.lower()

                docs = []
                doc = documents.get(evidence, None)
                if doc is not None:
                    docs.append(doc)

                if len(documentURL) > 0:
                    doc1 = documents.get(documentURL, res.evidence_context(Document)(uri=documentURL))
                    documents[documentURL] = doc1
                    docs.append(doc1)

                if relation in ('neurotransmitter', 'innexin', 'neuropeptide', 'receptor'):
                    for d in docs:
                        getattr(self.context_for(d)(Neuron)(neuron_name), relation)(data)
                elif relation == 'type':
                    _data = data.lower()
                    # type data aren't normalized so we check for strings within the _data string
                    types = [x for x in ('sensory', 'interneuron', 'motor', 'unknown') if x in _data]

                    for t in types:
                        for d in docs:
                            self.context_for(d)(Neuron)(neuron_name).type(t)
        for d in documents.values():
            contextualized_doc_ctx = res.evidence_context(self.context_for(d))
            res.evidence_context(Evidence)(reference=d, supports=contextualized_doc_ctx.rdf_object)
            res.data_context.add_import(contextualized_doc_ctx)
        return res

    def context_for(self, document):
        res = self.__document_contexts.get(document.identifier)
        if res is None:
            self.__document_contexts[document.identifier] = Context(ident=self.identifier + '/context_for?document=' + document.identifier)
            res = self.__document_contexts[document.identifier]
        return res


# TODO: Make PersonDataTranslators and Document/Website DataSource for the
# documents these come from. Need to verify who made the translation from the
# website / document
DATA_SOURCES = [
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
        bibtex_files=['../aux_data/bibtex_files/altun2009.bib',
                      '../aux_data/bibtex_files/WormAtlas.bib']),
    WormBaseCSVDataSource(
        key='WormBaseCSVDataSource',
        csv_file_name=CELL_NAMES_SOURCE),
    WormAtlasCellListDataSource(
        key='WormAtlasCellList',
        csv_file_name=LINEAGE_LIST_LOC),
    ConnectomeCSVDataSource(
        key='EmmonsConnectomeCSVDataSource',
        csv_file_name=CONNECTOME_SOURCE)
]

EXTRA_NEURON_SOURCES = []
for root, _, filenames in os.walk(ADDITIONAL_EXPR_DATA_DIR):
    for filename in sorted(filenames):
        if filename.lower().endswith('.csv'):
            name = 'NeuronCSVExpressionDataSource_' + os.path.basename(filename).rsplit('.', 1)[0]
            EXTRA_NEURON_SOURCES.append(NeuronCSVDataSource(csv_file_name=os.path.join(root, filename), key=name))

DATA_SOURCES += EXTRA_NEURON_SOURCES

DATA_SOURCES_BY_KEY = {x.key: x for x in DATA_SOURCES}

TRANS_MAP = [
    # ('WormbaseTextMatchCSVChannelNeuronDataSource',
     # WormbaseTextMatchCSVTranslator),
    # (('WormAtlasCellList', 'Neurons'),
     # WormAtlasCellListDataTranslator),
    # ('WormbaseTextMatchCSVChannelMuscleDataSource',
     # WormbaseTextMatchCSVTranslator),
    # ('WormbaseIonChannelCSVDataSource',
     # WormbaseIonChannelCSVTranslator),
    ('WormAtlasNeuronTypesSource',
     NeuronCSVDataTranslator,
     'Neurons'),
    # ('WormBaseCSVDataSource',
     # MuscleWormBaseCSVTranslator),
    (('EmmonsConnectomeCSVDataSource', 'Neurons'),
     NeuronConnectomeCSVTranslator),
    # ('WormBaseCSVDataSource',
     # NeuronWormBaseCSVTranslator)
]

# for s in EXTRA_NEURON_SOURCES:
    # TRANS_MAP.append((s.key, NeuronCSVDataTranslator))


def serialize_as_nquads():
    P.config('rdf.graph').serialize('../WormData.n4', format='nquads')
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


def do_insert(config="default.conf", logging=False):
    global WORM
    global DATA_SOURCES_BY_KEY

    P.connect(configFile=config, do_logging=logging)
    try:
        t0 = time()
        translators = dict()
        remaining = list(TRANS_MAP)
        last_remaining = None
        while remaining != last_remaining:
            next_remaining = []
            for t in remaining:
                if not isinstance(t[0], (list, tuple)):
                    source_keys = (t[0],)
                else:
                    source_keys = t[0]

                sources = tuple(DATA_SOURCES_BY_KEY.get(s) for s in source_keys)
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

                print('\n'.join(str(s) for s in sources))
                print('Translating with {}'.format(translator))
                res = translator(*sources, output_key=output_key)

                print('Result {}'.format(res))
                if res.key:
                    DATA_SOURCES_BY_KEY[res.key] = res
                else:
                    DATA_SOURCES_BY_KEY[res.identifier] = res
            last_remaining = list(remaining)
            remaining = next_remaining
        for x in remaining:
            warn("Failed to process: {}".format(x))

        # attach_neuromlfiles_to_channel()
        # upload_connections()

        t1 = time()
        print("Saving %d objects..." % IWCTX.size())
        for src in DATA_SOURCES_BY_KEY.values():
            if isinstance(src, DataWithEvidenceDataSource):
                print('saving', src)
                src.data_context.save_context(P.config('rdf.graph'), inline_imports=True)
                src.evidence_context.save_context(P.config('rdf.graph'), inline_imports=True)
                for ctx in src.contexts:
                    ctx.save_context(P.config('rdf.graph'))
        IWCTX.save_context(P.config('rdf.graph'), inline_imports=True)

        print("Saved %d objects." % IWCTX.defcnt)
        print("Saved %d triples." % IWCTX.tripcnt)
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

    do_insert(config=options.config, logging=options.do_logging)
