from __future__ import print_function
from time import time
from rdflib.namespace import Namespace
import PyOpenWorm as P
from PyOpenWorm.utils import normalize_cell_name
from PyOpenWorm.context import Context
from PyOpenWorm.bibtex import parse_bibtex_into_documents
# import logging
import traceback
import csv
import re
import os
from yarom import MAPPER

import PyOpenWorm.import_override as impo
impo.Overrider(MAPPER).wrap_import()
# logging.basicConfig(level=logging.DEBUG)
CTX = Context(ident="http://openworm.org/entities/bio#worm0-data",
              imported=(P.CONTEXT,))

from CTX.PyOpenWorm.channel import Channel
from CTX.PyOpenWorm.channel import ExpressionPattern
from CTX.PyOpenWorm.neuron import Neuron
from CTX.PyOpenWorm.muscle import Muscle
from CTX.PyOpenWorm.connection import Connection
from CTX.PyOpenWorm.network import Network
from CTX.PyOpenWorm.worm import Worm
from CTX.PyOpenWorm.cell import Cell

EVCTX = Context(ident="http://openworm.org/entities/bio#worm0-evidence",
                imported=(P.CONTEXT,))

from EVCTX.PyOpenWorm.evidence import Evidence
from EVCTX.PyOpenWorm.document import Document
from EVCTX.PyOpenWorm.website import Website
from EVCTX.PyOpenWorm.datasource import (DataTranslator, DataSource, Informational, Translation)

IWCTX = Context(ident="http://openworm.org/entities/bio#worm0",
                imported=(CTX, EVCTX))

LINEAGE_LIST_LOC = '../aux_data/C. elegans Cell List - WormAtlas.tsv'
WORM = None
NETWORK = None
OPTIONS = None
CELL_NAMES_SOURCE = "../aux_data/C. elegans Cell List - WormBase.csv"
CONNECTOME_SOURCE = "../aux_data/herm_full_edgelist.csv"
IONCHANNEL_SOURCE = "../aux_data/ion_channel.csv"
CHANNEL_MUSCLE_SOURCE = "../aux_data/Ion channels - Ion Channel To Body Muscle.tsv"
CHANNEL_NEURON_SOURCE = "../aux_data/Ion channels - Ion Channel To Neuron.tsv"
CHANNEL_NEUROMLFILE = "../aux_data/NeuroML_Channel.csv"
NEURON_EXPRESSION_DATA_SOURCE = "../aux_data/Modified celegans db dump.csv"

ADDITIONAL_EXPR_DATA_DIR = '../aux_data/expression_data'
TRANS_NS = Namespace('http://openworm.org/entities/translators/')
DS_NS = Namespace('http://openworm.org/entities/data_sources/')

class LocalFileDataSource(DataSource):
    file_name = Informational(display_name='File name')


class CSVDataSource(LocalFileDataSource):
    rdf_namespace = Namespace(DS_NS['CSVDataSource#'])

    csv_file_name = Informational(display_name='CSV file name',
                                  also=LocalFileDataSource.file_name)
    csv_header = Informational(display_name='Header column names', multiple=False)

    csv_field_delimiter = Informational(display_name='CSV field delimiter')

class WormbaseTextMatchCSVDataSource(CSVDataSource):
    rdf_namespace = Namespace(DS_NS['WormbaseTextMatchCSVDataSource#'])

    def __init__(self, cell_type, initial_cell_column, **kwargs):
        """
        Parameters
        ----------
        cell_type : type
            The type of cell to generate
        initial_cell_column : int
            The index of the first column with a cell name
        """
        super(WormbaseTextMatchCSVDataSource, self).__init__(**kwargs)
        self.cell_type = cell_type
        self.initial_cell_column = initial_cell_column


class WormbaseIonChannelCSVDataSource(CSVDataSource):

    rdf_namespace = Namespace(DS_NS['WormbaseTextMatchCSVDataSource#'])

    csv_header = ['channel_name',
                  'gene_name',
                  'gene_WB_ID',
                  'expression_pattern',
                  'description']


class DataWithEvidenceDataSource(DataSource):
    evidence_context = Informational(display_name='Evidence context',
                                     description='The context in which evidence for the "Data context" is defined')
    data_context = Informational(display_name='Data context',
                                 description='The context in which primary data for this data source is defined')
    contexts = Informational(display_name='Other contexts',
                             description='Other contexts defined by the data translator')
    rdf_namespace = Namespace(DS_NS['DataWithEvidenceDataSource#'])
    def __init__(self, *args, **kwargs):
        super(DataWithEvidenceDataSource, self).__init__(*args, **kwargs)
        # print(self.translation._v)
        self.data_context = Context(ident=self.identifier + '-data',
                                    imported=(P.CONTEXT,))
        self.evidence_context = Context(ident=self.identifier + '-evidence',
                                        imported=(P.CONTEXT,))
        self.contexts = []



class NeuronCSVDataSource(CSVDataSource):
    rdf_namespace = Namespace(DS_NS['NeuronCSVDataSource#'])
    bibtex_files = Informational(display_name='BibTeX files',
                                 description='List of BibTeX files that are referenced in the csv file by entry ID')


class CSVDataTranslator(DataTranslator):

    def make_reader(self, source):
        params = dict()
        if source.csv_field_delimiter.has_defined_value():
            params['delimiter'] = source.csv_field_delimiter.onedef()

        params['skipinitialspace'] = True

        return csv.reader(source.csv_file_name.onedef(), **params)

class WormbaseIonChannelCSVTranslator(DataTranslator):
    input_type = WormbaseIonChannelCSVDataSource
    output_type = DataWithEvidenceDataSource
    translator_identifier = TRANS_NS.WormbaseIonChannelCSVTranslator

    def translate(self, data_source):
        res = self.make_new_output((data_source,))
        try:
            with open(data_source.csv_file_name.onedef(), 'r') as csvfile:
                next(csvfile, None)
                csvreader = csv.reader(csvfile, skipinitialspace=True)
                with res.data_context(Channel=Channel, ExpressionPattern=ExpressionPattern) as ctx:
                    for line in csvreader:
                        channel_name = normalize_cell_name(line[0]).upper()
                        gene_name = line[1].upper()
                        gene_WB_ID = line[2].upper()
                        expression_pattern = line[3]
                        description = line[4]
                        c = ctx.Channel(name=str(channel_name))
                        c.gene_name(gene_name)
                        c.gene_WB_ID(gene_WB_ID)
                        c.description(description)
                        patterns = expression_pattern.split(r' | ')
                        regex = re.compile(r' *\[([^\]]+)\] *(.*) *')

                        matches = [regex.match(pat) for pat in patterns]
                        patterns = [ctx.ExpressionPattern(wormbaseID=m.group(1),
                                                          description=m.group(2))
                                    for m in matches if m is not None]
                        for pat in patterns:
                            c.expression_pattern(pat)
        except Exception:
            traceback.print_exc()
        return res


class WormbaseTextMatchCSVTranslator(DataTranslator):
    input_type = WormbaseTextMatchCSVDataSource
    output_type = DataWithEvidenceDataSource
    translator_identifier = TRANS_NS.WormbaseTextMatchCSVTranslator

    def translate(self, data_source):
        initcol = data_source.initial_cell_column
        ctype = data_source.cell_type
        res = self.make_new_output((data_source,))
        try:
            with open(data_source.csv_file_name.onedef(), 'r') as f:
                reader = csv.reader(f, delimiter='\t')
                header = self.skip_to_header(reader)
                with res.data_context(Channel=Channel) as ctx:
                    for row in reader:
                        cells = self.extract_cell_names(header,
                                                        initcol,
                                                        row)
                        ch = ctx.Channel(name=str(row[0]))
                        for cell in cells:
                            m = ctype(name=str(cell))
                            ch.appearsIn(m)
        except Exception:
            traceback.print_exc()
        return res

    def skip_to_header(self, reader):
        rows = 0
        for row in reader:
            if rows == 3:
                return row
            rows += 1
        return None

    def extract_cell_names(self, header, initial_cell_column, row):
        res = []
        cols = 0
        for col in row:
            if cols > initial_cell_column:
                if col == '1' or col == '2':
                    res.append(header[cols])
            cols += 1
        return res


class NeuronCSVDataTranslator(DataTranslator):
    input_type = NeuronCSVDataSource
    output_type = DataWithEvidenceDataSource
    translator_identifier = TRANS_NS.NeuronCSVDataTranslator

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
                        getattr(d.as_context(Neuron)(neuron_name), relation)(data)
                elif relation == 'type':
                    _data = data.lower()
                    # type data aren't normalized so we check for strings within the _data string
                    types = [x for x in ('sensory', 'interneuron', 'motor', 'unknown') if x in _data]

                    for t in types:
                        for d in docs:
                            d.as_context(Neuron)(neuron_name).type(t)
        for d in documents.values():
            contextualized_doc_ctx = res.evidence_context(d.as_context)
            res.evidence_context(Evidence)(reference=d, supports=contextualized_doc_ctx.rdf_object)
            res.contexts.append(d.as_context)
        return res


class WormBaseCSVDataSource(CSVDataSource):
    rdf_namespace = Namespace(DS_NS['MuscleCSVDataSource#'])
    csv_header = ["Cell",
                  "Lineage Name",
                  "Description",
                  "Total count of identified adult-only hermaphrodite cells",
                  "Total count of adult-only male cells",
                  "Neurons (no male-specific cells)",
                  "Neurons (male-specific)",
                  "Body wall muscles",
                  "Pharynx muscles",
                  "Other muscles",
                  "Other adult-only cells in the hermaphrodite",
                  "Other adult-only hermaphrodite-specific cells (not present in males)",
                  "Motor neurons related to body wall muscles",
                  "Embryonic cells not present in adult",
                  "Male-specific cells",
                  "Male-specific adult-only cells",
                  "Cells with non-unique name",
                  "",
                  "VirtualWorm blender model names",
                  "WormBase ID",
                  "Synonyms"]


class WormAtlasCellListDataSource(CSVDataSource):
    rdf_namespace = Namespace(DS_NS['WormAtlasCellListDataSource#'])
    csv_header = ['Cell', 'Lineage Name', 'Description']


class MuscleWormBaseCSVTranslator(DataTranslator):
    input_type = WormBaseCSVDataSource
    output_type = DataWithEvidenceDataSource
    translator_identifier = TRANS_NS.MuscleWormBaseCSVTranslator

    def translate(self, data_source):
        """ Upload muscles and the neurons that connect to them """
        res = self.make_new_output((data_source,))
        with open(data_source.csv_file_name.onedef()) as csvfile:
            csvreader = csv.reader(csvfile)

            # TODO: Improve this evidence by going back to the actual research
            #       by using the wormbase REST API in addition to or instead of the CSV file
            with res.evidence_context(Evidence=Evidence, Website=Website) as ctx:
                doc = ctx.Website(key="wormbase", url="Wormbase.org", title="WormBase")
                ctx.Evidence(reference=doc, supports=doc.as_context.rdf_object)

            with doc.as_context(Worm=Worm, Muscle=Muscle) as ctx:
                w = ctx.Worm()

                for num, line in enumerate(csvreader):
                    if num < 4:  # skip rows with no data
                        continue

                    if line[7] or line[8] or line[9] == '1':  # muscle's marked in these columns
                        muscle_name = normalize_cell_name(line[0]).upper()
                        m = ctx.Muscle(name=muscle_name)
                        w.muscle(m)
        return res


class NeuronWormBaseCSVTranslator(DataTranslator):
    input_type = WormBaseCSVDataSource
    output_type = DataWithEvidenceDataSource
    translator_identifier = TRANS_NS.NeuronWormBaseCSVTranslator
    def translate(self, data_source):
        res = self.make_new_output((data_source,))
        # TODO: Improve this evidence by going back to the actual research
        #       by using the wormbase REST API in addition to or instead of the CSV file
        with res.evidence_context(Evidence=Evidence, Website=Website) as ctx:
            doc = ctx.Website(key="wormbase", url="Wormbase.org", title="WormBase")
            ctx.Evidence(reference=doc, supports=doc.as_context.rdf_object)

        with res.data_context(Worm=Worm, Network=Network, Neuron=Neuron) as ctx:
            w = ctx.Worm()
            n = ctx.Network()
            w.neuron_network(n)
            n.worm(w)

            with open(data_source.csv_file_name.onedef()) as csvfile:
                csvreader = csv.reader(csvfile)

                for num, line in enumerate(csvreader):
                    if num < 4:  # skip rows with no data
                        continue

                    if line[5] == '1':  # neurons marked in this column
                        neuron_name = normalize_cell_name(line[0]).upper()
                        n.neuron(ctx.Neuron(name=neuron_name))
        return res


class WormAtlasCellListDataTranslation(Translation):
    def __init__(self, **kwargs):
        super(WormAtlasCellListDataTranslation, self).__init__(**kwargs)
        self.neurons_source = WormAtlasCellListDataTranslation.ObjectProperty()


class WormAtlasCellListDataTranslator(CSVDataTranslator):
    input_type = (WormAtlasCellListDataSource, DataWithEvidenceDataSource)
    output_type = DataWithEvidenceDataSource
    translation_type = WormAtlasCellListDataTranslation
    translator_identifier = TRANS_NS.WormAtlasCellListDataTranslator

    def translate(self, data_source, neurons_source):
        # XXX: This wants a way to insert cells, then later, to insert neurons from the same set
        # and have the later recoginzed as the former. Identifier matching limits us here. It would
        # be best to establish owl:sameAs links to the super class (Cell) from the subclass (Neuron)
        # at the sub-class insert and have a reasoner relate
        # the two sets of inserts.
        res = self.make_new_output(sources=(data_source, neurons_source))
        tr = res.translation.onedef()
        tr.neurons_source(neurons_source)
        try:
            net = neurons_source.data_context(Network)()
            w = res.data_context(Worm)()
            # TODO: Improve this evidence marker
            doc = res.evidence_context(Website)(url="http://www.wormatlas.org/celllist.htm")
            doc_ctx = doc.as_context
            with open(data_source.csv_file_name.onedef(), "r") as cell_data:

                # Skip headers
                next(cell_data)

                self.make_reader(data_source)
                csvreader = csv.reader(cell_data, skipinitialspace=True)
                cell_name_counters = dict()
                data = dict()
                for j in csvreader:
                    print(j)
                    name = j[0]
                    lineageName = j[1]
                    desc = j[2]

                    # XXX: These renaming choices are arbitrary; may be inappropriate
                    if name == "DB1/3":
                        name = "DB1"
                    elif name == "DB3/1":
                        name = "DB3"
                    elif name == "AVFL/R":
                        if lineageName[0] == "W":
                            name = "AVFL"
                        elif lineageName[0] == "P":
                            name = "AVFR"

                    if name in cell_name_counters:
                        basename = name
                        while name in cell_name_counters:
                            cell_name_counters[basename] += 1
                            name = basename + "(" + str(cell_name_counters[basename]) + ")"
                    else:
                        cell_name_counters[name] = 0

                    data[name] = {"lineageName": lineageName, "desc": desc}

            for n in net.neurons():
                # Get the name of the neuron in its original context
                name = n.name.one()
                cell_data = data[str(name)]
                # Make statements in the result context
                nn = res.data_context(n)
                nn.lineageName(cell_data['lineageName'])
                nn.description(cell_data['desc'])
                w.cell(nn)

            # TODO: Add data for other cells here. Requires relating named
            # muscle cells to their counterparts in the cell list (e.g. mu_bod(#))
            # Also requires removing neurons and muscles from the list once
            # they've been identified so they aren't stored twice

            # ev.supports(w)
            print ("uploaded lineage and descriptions")
        except Exception:
            traceback.print_exc()
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
        csv_file_name=LINEAGE_LIST_LOC)
    ] + [NeuronCSVDataSource(csv_file_name=os.path.join(root, filename), key='NeuronCSVExpressionDataSource_' + os.path.basename(filename).rsplit('.', 1)[0])
         for root, _, filenames in os.walk(ADDITIONAL_EXPR_DATA_DIR)
         for filename in sorted(filenames)
         if filename.lower().endswith('.csv')]

DATA_SOURCES_BY_KEY = {x.key: x for x in DATA_SOURCES}

TRANS_MAP = [
    # ('WormbaseTextMatchCSVChannelNeuronDataSource',
     # WormbaseTextMatchCSVTranslator),
    # ('WormbaseTextMatchCSVChannelMuscleDataSource',
     # WormbaseTextMatchCSVTranslator),
    # ('WormbaseIonChannelCSVDataSource',
     # WormbaseIonChannelCSVTranslator),
    ('WormAtlasNeuronTypesSource',
     NeuronCSVDataTranslator,
     'Neurons'),
    # ('WormBaseCSVDataSource',
     # MuscleWormBaseCSVTranslator),
    # ('WormBaseCSVDataSource',
     # NeuronWormBaseCSVTranslator),
    (('WormAtlasCellList', 'Neurons'),
     WormAtlasCellListDataTranslator)
]


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


def translate(data_source):

    print ("uploading statements about connections")

    # to normalize certian body wall muscle cell names
    SEARCH_STRING_MUSCLE = re.compile(r'\w+[BWM]+\w+')
    REPLACE_STRING_MUSCLE = re.compile(r'[BWM]+')

    def normalize_muscle(name):
        # normalize names of Body Wall Muscles
        # if there is 'BWM' in the name, remove it
        if re.match(SEARCH_STRING_MUSCLE, name):
            name = REPLACE_STRING_MUSCLE.sub('', name)
        return name

    # muscle cells that are generically defined in source and need to be broken
    # into pair of L and R before being added to PyOpenWorm
    to_expand_muscles = ['PM1D', 'PM2D', 'PM3D', 'PM4D', 'PM5D']

    # muscle cells that have different names in connectome source and cell list.
    # Their wormbase cell list names will be used in PyOpenWorm
    changed_muscles = ['ANAL', 'INTR', 'INTL', 'SPH']

    def changed_muscle(x):
        return {
            'ANAL': 'MU_ANAL',
            'INTR': 'MU_INT_R',
            'INTL': 'MU_INT_L',
            'SPH': 'MU_SPH'
        }[x]

    def expand_muscle(name):
        return Muscle(name + 'L'), Muscle(name + 'R')

    # cells that are neither neurons or muscles. These are marked as
    # 'Other Cells' in the wormbase cell list but are still part of the new
    # connectome.
    #
    # TODO: In future work these should be uploaded seperately to
    # PyOpenWorm in a new upload function and should be referred from there
    # instead of this list.
    other_cells = ['MC1DL', 'MC1DR', 'MC1V', 'MC2DL', 'MC2DR', 'MC2V', 'MC3DL',
                   'MC3DR', 'MC3V']

    # counters for terminal printing
    neuron_connections = 0
    muscle_connections = 0
    other_connections = 0

    try:
        w = WORM
        n = NETWORK

        neuron_objs = list(set(n.neurons()))
        muscle_objs = list(w.muscles())

        w.neuron_network(n)

        # get lists of neuron and muscles names
        neurons = [neuron.name() for neuron in neuron_objs]
        muscles = [muscle.name() for muscle in muscle_objs]

        # Evidence object to assert each connection
        e = Evidence(key="emmons2015", title='herm_full_edgelist.csv')

        with open(CONNECTOME_SOURCE) as csvfile:
            edge_reader = csv.reader(csvfile)
            next(edge_reader)    # skip header row
            for row in edge_reader:
                source, target, weight, syn_type = map(str.strip, row)

                # set synapse type to something the Connection object
                # expects, and normalize the source and target names
                if syn_type == 'electrical':
                    syn_type = 'gapJunction'
                elif syn_type == 'chemical':
                    syn_type = 'send'

                source = normalize_cell_name(source).upper()
                target = normalize_cell_name(target).upper()

                weight = int(weight)

                # remove BMW from Body Wall Muscle cells
                if 'BWM' in source:
                    source = normalize_muscle(source)
                if 'BWM' in target:
                    target = normalize_muscle(target)

                # change certain muscle names to names in wormbase
                if source in changed_muscles:
                    source = changed_muscle(source)
                if target in changed_muscles:
                    target = changed_muscle(target)

                def marshall(name):
                    ret = []
                    res = None
                    res2 = None
                    if name in neurons:
                        res = Neuron(name)
                    elif name in muscles:
                        res = Muscle(name)
                    elif name in to_expand_muscles:
                        res, res2 = expand_muscle(name)
                    elif name in other_cells:
                        res = Cell(name)

                    if res is not None:
                        ret.append(res)
                    if res2 is not None:
                        ret.append(res2)

                    return ret

                def add_synapse(source, target):
                    c = Connection(pre_cell=source, post_cell=target,
                                   number=weight, syntype=syn_type)
                    n.synapse(c)
                    e.supports(c)

                    if isinstance(source, Neuron) and isinstance(target, Neuron):
                        c.termination('neuron')
                    elif isinstance(source, Neuron) and isinstance(target, Muscle):
                        c.termination('muscle')
                    elif isinstance(source, Muscle) and isinstance(target, Neuron):
                        c.termination('muscle')

                    return c

                sources = marshall(source)
                targets = marshall(target)

                for s in sources:
                    for t in targets:
                        conn = add_synapse(s, t)
                        kind = conn.termination()
                        if kind == 'muscle':
                            muscle_connections += 1
                        elif kind == 'neuron':
                            neuron_connections += 1
                        else:
                            other_connections += 1

        e.supports(n)  # assert the whole connectome too
        print('Total neuron to neuron connections added = %i' % neuron_connections)
        print('Total neuron to muscle connections added = %i' % muscle_connections)
        print('Total other connections added = %i' % other_connections)
        print('uploaded connections')

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
    global NETWORK
    global DATA_SOURCES_BY_KEY

    if config:
        if isinstance(config, P.Configure):
            pass
        elif isinstance(config, str):
            config = P.Configure.open(config)
        elif isinstance(config, dict):
            config = P.Configure().copy(config)
        else:
            raise Exception("Invalid configuration object " + str(config))

    P.connect(conf=config, do_logging=logging)
    try:
        t0 = time()
        translators = dict()
        for t in TRANS_MAP:
            if not isinstance(t[0], (list, tuple)):
                source_keys = (t[0],)
            else:
                source_keys = t[0]

            sources = tuple(DATA_SOURCES_BY_KEY[s] for s in source_keys)
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
            res = translator.translate(*sources)

            if output_key:
                res.key = output_key
            print('Result {}'.format(res))
            if res.key:
                DATA_SOURCES_BY_KEY[res.key] = res


        # attach_neuromlfiles_to_channel()
        # upload_lineage_and_descriptions()
        # upload_connections()

        t1 = time()
        print("Saving %d objects..." % IWCTX.size())
        for src in (s for s in DATA_SOURCES_BY_KEY.values()
                    if isinstance(s, DataWithEvidenceDataSource)):
            src.data_context.save_context(P.config('rdf.graph'))
            src.evidence_context.save_context(P.config('rdf.graph'))
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
