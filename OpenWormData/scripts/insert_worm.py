from __future__ import print_function
from time import time
import PyOpenWorm as P
from PyOpenWorm.utils import normalize_cell_name
from PyOpenWorm.datasource import DataTranslator, DataSource
from PyOpenWorm.dataObject import Context
import traceback
import csv
import re
import os


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
RECEPTORS_TYPES_NEUROPEPTIDES_NEUROTRANSMITTERS_INNEXINS_SOURCE = "../aux_data/Modified celegans db dump.csv"

ADDITIONAL_EXPR_DATA_DIR = '../aux_data/expression_data'


class CSVDataSource(DataSource):
    def __init__(self, csv_file_name, header=None, **kwargs):
        super(CSVDataSource, self).__init__(**kwargs)
        self.csv_file_name = csv_file_name
        self.header = header


class WormbaseTextMatchCSVDataSource(CSVDataSource):
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
    def __init__(self, **kwargs):
        super(WormbaseIonChannelCSVDataSource, self).__init__(
                header=['channel_name',
                        'gene_name',
                        'gene_WB_ID',
                        'expression_pattern',
                        'description'],
                **kwargs)


class WormbaseIonChannelCSVTranslator(DataTranslator):
    data_source_type = WormbaseIonChannelCSVDataSource

    def translate(self, data_source):
        res = set([])
        try:
            with open(data_source.csv_file_name) as csvfile:
                next(csvfile, None)
                csvreader = csv.reader(csvfile, skipinitialspace=True)

                for line in csvreader:
                    channel_name = normalize_cell_name(line[0]).upper()
                    gene_name = line[1].upper()
                    gene_WB_ID = line[2].upper()
                    expression_pattern = line[3]
                    description = line[4]
                    c = P.Channel(name=str(channel_name))
                    c.gene_name(gene_name)
                    c.gene_WB_ID(gene_WB_ID)
                    c.description(description)
                    patterns = expression_pattern.split(r' | ')
                    regex = re.compile(r' *\[([^\]]+)\] *(.*) *')

                    matches = [regex.match(pat) for pat in patterns]
                    patterns = [P.ExpressionPattern(wormbaseID=m.group(1),
                                                    description=m.group(2))
                                for m in matches if m is not None]
                    for pat in patterns:
                        c.expression_pattern(pat)
                    res.add(c)
        except Exception:
            traceback.print_exc()
        return res


class WormbaseTextMatchCSVTranslator(DataTranslator):
    data_source_type = WormbaseTextMatchCSVDataSource

    def translate(self, data_source):
        initcol = data_source.initial_cell_column
        ctype = data_source.cell_type
        res = set([])
        try:
            with open(data_source.csv_file_name, 'rb') as f:
                reader = csv.reader(f, delimiter='\t')
                header = self.skip_to_header(reader)
                for row in reader:
                    cells = self.extract_cell_names(header,
                                                    initcol,
                                                    row)
                    ch = P.Channel(name=str(row[0]))
                    for cell in cells:
                        m = ctype(name=str(cell))
                        res.add(ch.appearsIn(m))
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

DATA_SOURCES = [ WormbaseTextMatchCSVDataSource( cell_type=P.Neuron
                                               , csv_file_name=CHANNEL_NEURON_SOURCE
                                               , initial_cell_column=101)
               , WormbaseTextMatchCSVDataSource( cell_type=P.Muscle
                                               , csv_file_name=CHANNEL_MUSCLE_SOURCE
                                               , initial_cell_column=6)
               , WormbaseIonChannelCSVDataSource(csv_file_name=IONCHANNEL_SOURCE)
               ]

TRANSLATORS = [ WormbaseTextMatchCSVTranslator()
              , WormbaseIonChannelCSVTranslator()
              ]

def serialize_as_n3():
    dest = '../WormData.n3'
    # XXX: Properties aren't initialized until the first object of a class is
    #      created, so we create them here

    P.config('rdf.graph').serialize(dest, format='n3')
    print('serialized to n3 file')


def attach_neuromlfiles_to_channel():
    """ attach the links to the neuroml files for the ion channels
    """
    print("attaching links to neuroml files")
    try:
        with open(CHANNEL_NEUROMLFILE) as csvfile:
            next(csvfile, None)
            csvreader = csv.reader(csvfile, skipinitialspace=True)
            for row in csvreader:
                ch = P.Channel(name=str(row[0]))
                ch.neuroML_file(str(row[1]))
                ch.save()
        print("neuroML file links attached")
    except Exception:
        traceback.print_exc()


def upload_ionchannels():
    """ Upload muscles and the neurons that connect to them
    """
    print ("uploading the ion channels")
    res = set([])
    try:
        with open(IONCHANNEL_SOURCE) as csvfile:
            next(csvfile, None)
            csvreader = csv.reader(csvfile, skipinitialspace=True)

            for num, line in enumerate(csvreader):
                channel_name = normalize_cell_name(line[0]).upper()
                gene_name = line[1].upper()
                gene_WB_ID = line[2].upper()
                expression_pattern = line[3]
                description = line[4]
                c = P.Channel(name=str(channel_name))
                c.gene_name(gene_name)
                c.gene_WB_ID(gene_WB_ID)
                c.description(description)
                patterns = expression_pattern.split(r' | ')
                regex = re.compile(r' *\[([^\]]+)\] *(.*) *')

                matches = [regex.match(pat) for pat in patterns]
                patterns = [P.ExpressionPattern(wormbaseID=m.group(1),
                                                description=m.group(2))
                            for m in matches if m is not None]
                for pat in patterns:
                    c.expression_pattern(pat)
                res.add(c)
        print ("uploaded ion_channel")
    except Exception:
        traceback.print_exc()
    return res


def extract_neuron_names(heading, row):
    FIRST_NEURON_NAME_COL = 101
    neuronlist = []
    cols = 0
    for col in row:
        if cols <= FIRST_NEURON_NAME_COL:
            cols += 1
        else:
            if col == '1' or col == '2':
                neuronlist.append(heading[cols])
            cols += 1
    return neuronlist


def extract_muscle_names(heading, row):
    FIRST_MUSCLE_NAME_COL = 6
    musclelist = []
    cols = 0
    for col in row:
        if cols <= FIRST_MUSCLE_NAME_COL:
            cols += 1
        else:
            if col == '1' or col == '2':
                musclelist.append(heading[cols])
            cols += 1
    return musclelist


def upload_muscles():
    """ Upload muscles and the neurons that connect to them
    """
    try:
        with open(CELL_NAMES_SOURCE) as csvfile:
            csvreader = csv.reader(csvfile)

            ev = P.Evidence(key="wormbase", title="C. elegans Cell List - WormBase.csv")
            w = WORM
            for num, line in enumerate(csvreader):
                if num < 4:  # skip rows with no data
                    continue

                if line[7] or line[8] or line[9] == '1':  # muscle's marked in these columns
                    muscle_name = normalize_cell_name(line[0]).upper()
                    m = P.Muscle(name=muscle_name)
                    w.muscle(m)
            ev.asserts(w)
        #second step, get the relationships between them and add them to the graph
        print ("uploaded muscles")
    except Exception:
        traceback.print_exc()


def upload_lineage_and_descriptions():
    """ Upload lineage names and descriptions pulled from the WormAtlas master cell list

    Assumes that Neurons and Muscles have already been added
    """
    # XXX: This wants a way to insert cells, then later, to insert neurons from the same set
    # and have the later recoginzed as the former. Identifier matching limits us here. It would
    # be best to establish owl:sameAs links to the super class (Cell) from the subclass (Neuron)
    # at the sub-class insert and have a reasoner relate
    # the two sets of inserts.
    try:
        w = WORM
        net = NETWORK
        # TODO: Improve this evidence marker
        ev = P.Evidence(uri="http://www.wormatlas.org/celllist.htm")
        cell_data = open(LINEAGE_LIST_LOC, "r")

        # Skip headers
        next(cell_data)

        cell_name_counters = dict()
        data = dict()
        for x in cell_data:
            j = [x.strip().strip("\"") for x in x.split("\t")]
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
                while (name in cell_name_counters):
                    cell_name_counters[name] += 1
                    name = name + "(" + str(cell_name_counters[name]) + ")"
            else:
                cell_name_counters[name] = 0

            data[name] = {"lineageName": lineageName, "desc": desc}

        def add_data_to_cell(n):
            name = n.name.one()
            cell_data = data[str(name)]
            n.lineageName(cell_data['lineageName'])
            n.description(cell_data['desc'])
            w.cell(n)

        for n in net.neurons():
            add_data_to_cell(n)

        # TODO: Add data for other cells here. Requires relating named
        # muscle cells to their counterparts in the cell list (e.g. mu_bod(#))
        # Also requires removing neurons and muscles from the list once
        # they've been identified so they aren't stored twice

        ev.asserts(w)
        print ("uploaded lineage and descriptions")
    except Exception:
        traceback.print_exc()


def norn(x):
    """ return the next or None of an iterator """
    try:
        return next(x)
    except StopIteration:
        return None


def upload_neurons():
    try:
        #TODO: Improve this evidence marker
        ev = P.Evidence(key="wormbase", title="C. elegans Cell List - WormBase.csv")
        w = WORM
        n = NETWORK
        w.neuron_network(n)
        # insert neurons.
        i = 0
        with open(CELL_NAMES_SOURCE) as csvfile:
            csvreader = csv.reader(csvfile)

            for num, line in enumerate(csvreader):
                if num < 4:  # skip rows with no data
                    continue

                if line[5] == '1':  # neurons marked in this column
                    neuron_name = normalize_cell_name(line[0]).upper()
                    n.neuron(P.Neuron(name=neuron_name))
                    i = i + 1

        ev.asserts(n)
        #second step, get the relationships between them and add them to the graph
        print ("uploaded " + str(i) + " neurons")
    except Exception:
        traceback.print_exc()


def customizations(record):
    from bibtexparser.customization import author, link, doi
    """Use some functions delivered by the library

    :param record: a record
    :returns: -- customized record
    """
    return doi(link(author(record)))


def parse_bibtex_into_evidence(file_name):
    import bibtexparser
    e = None
    res = dict()
    with open(file_name) as bibtex_file:
        parser = bibtexparser.bparser.BibTexParser()
        parser.customization = customizations
        bib_database = bibtexparser.load(bibtex_file, parser=parser)
        for entry in bib_database.entries:
            key = entry['ID']
            e = P.Evidence(key=key)

            doi = entry.get('doi', None)
            if doi:
                e.doi(doi)

            author = entry.get('author', ())
            for ath in author:
                e.author(ath)

            title = entry.get('title', None)
            if title:
                e.title(title)

            year = entry.get('year', None)
            if year:
                e.year(year)

            res[key] = e
    return res




def upload_receptors_types_neurotransmitters_neuropeptides_innexins():
    """ Augment the metadata about neurons with information about receptors,
        neuron types, neurotransmitters, neuropeptides and innexins.
        As we go, add evidence objects to each statement."""
    print ("uploading statements about types, receptors, innexins, neurotransmitters and neuropeptides")

    _upload_receptors_types_neurotransmitters_neuropeptides_innexins_from_file(
        RECEPTORS_TYPES_NEUROPEPTIDES_NEUROTRANSMITTERS_INNEXINS_SOURCE
    )


def upload_additional_receptors_neurotransmitters_neuropeptides_innexins():
    """ Augment the metadata about neurons with information about receptor, neurotransmitter, and neuropeptide
    expression from additional sources.
    """
    print ("uploading additional statements about receptors, neurotransmitters and neuropeptides")

    for root, _, filenames in sorted(os.walk(ADDITIONAL_EXPR_DATA_DIR)):
        for filename in sorted(filenames):
            if filename.lower().endswith('.csv'):
                _upload_receptors_types_neurotransmitters_neuropeptides_innexins_from_file(os.path.join(root, filename))


def _upload_receptors_types_neurotransmitters_neuropeptides_innexins_from_file(file_path):
    # set up evidence objects in advance
    #

    evidences = dict()
    bibtex_files = ('../aux_data/bibtex_files/altun2009.bib',
                    '../aux_data/bibtex_files/WormAtlas.bib')
    for bib in bibtex_files:
        evidences.update(parse_bibtex_into_evidence(bib))

    i = 0

    uris = dict()

    with open(file_path) as f:
        reader = csv.reader(f)
        next(reader)  # skip the header row

        for row in reader:
            neuron_name = row[0]
            relation = row[1].lower()
            data = row[2]
            evidence = row[3]
            evidenceURL = row[4]

            e = evidences.get(evidence, None)

            e2 = uris.get(evidenceURL, None)
            if not e2:
                e2 = P.Evidence(uri=evidenceURL)
                uris[evidenceURL] = e2

            # grab the neuron object
            n = P.Neuron(neuron_name)
            NETWORK.neuron(n)

            if relation in ('neurotransmitter',
                            'innexin',
                            'neuropeptide',
                            'receptor'):
                r = getattr(n, relation)(data)
                if e:
                    e.asserts(r)
                if e2:
                    e2.asserts(r)
            elif relation == 'type':
                types = []
                if 'sensory' in (data.lower()):
                    types.append('sensory')
                if 'interneuron' in (data.lower()):
                    types.append('interneuron')
                if 'motor' in (data.lower()):
                    types.append('motor')
                if 'unknown' in (data.lower()):
                    types.append('unknown')
                # assign the data, grab the relation into r
                for t in types:
                    r = n.type(t)
                    # assert the evidence on the relationship
                    if e:
                        e.asserts(r)
                    if e2:
                        e2.asserts(r)
            i += 1
    print(
        'uploaded {} statements about types, receptors, innexins, neurotransmitters and neuropeptides from {}'.format(
            i, file_path
        )
    )


def upload_connections():

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
        return P.Muscle(name + 'L'), P.Muscle(name + 'R')

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
        e = P.Evidence(key="emmons2015", title='herm_full_edgelist.csv')

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
                        res = P.Neuron(name)
                    elif name in muscles:
                        res = P.Muscle(name)
                    elif name in to_expand_muscles:
                        res, res2 = expand_muscle(name)
                    elif name in other_cells:
                        res = P.Cell(name)

                    if res is not None:
                        ret.append(res)
                    if res2 is not None:
                        ret.append(res2)

                    return ret

                def add_synapse(source, target):
                    c = P.Connection(pre_cell=source, post_cell=target,
                                     number=weight, syntype=syn_type)
                    n.synapse(c)
                    e.asserts(c)

                    if isinstance(source, P.Neuron) and isinstance(target, P.Neuron):
                        c.termination('neuron')
                    elif isinstance(source, P.Neuron) and isinstance(target, P.Muscle):
                        c.termination('muscle')
                    elif isinstance(source, P.Muscle) and isinstance(target, P.Neuron):
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

        e.asserts(n)  # assert the whole connectome too
        print('Total neuron to neuron connections added = %i' %neuron_connections)
        print('Total neuron to muscle connections added = %i' %muscle_connections)
        print('Total other connections added = %i' %other_connections)
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
        semnet = w.rdf #fetches the entire worm.db graph

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

        ###uncomment next 4 lines to print inferred facts to human-readable file (demo purposes)
        #inferred_facts = closureDeltaGraph.serialize(format='n3') #format inferred facts to notation 3
        #inferred = open('what_was_inferred.n3', 'w')
        #inferred.write(inferred_facts)
        #inferred.close()

    except Exception:
        traceback.print_exc()
    print ("filled in with inferred data")


def do_insert(config="default.conf", logging=False):
    global WORM
    global NETWORK

    if config:
        if isinstance(config, P.Configure):
            pass
        elif isinstance(config, str):
            config = P.Configure.open(config)
        elif isinstance(config, dict):
            config = P.Configure().copy(config)
        else:
            raise Exception("Invalid configuration object "+ str(config))

    P.connect(conf=config, do_logging=logging)
    try:
        WORM = P.Worm()

        NETWORK = P.Network()
        WORM.neuron_network(NETWORK)
        NETWORK.worm(WORM)
        c = Context(key="insert_worm")
        t0 = time()
        upload_neurons()
        upload_muscles()
        for ds in DATA_SOURCES:
            best_translator = None
            for tr in TRANSLATORS:
                if isinstance(ds, tr.data_source_type):
                    if best_translator is None \
                        or issubclass(tr.data_source_type, best_translator.data_source_type):
                        best_translator = tr
            if best_translator is not None:
                c.add_objects(best_translator.translate(ds))

        c.add_objects([c, NETWORK])
        #attach_neuromlfiles_to_channel()
        #upload_lineage_and_descriptions()
        upload_connections()
        #upload_receptors_types_neurotransmitters_neuropeptides_innexins()
        #upload_additional_receptors_neurotransmitters_neuropeptides_innexins()

        #WORM.save()
        t1 = time()
        print("Saving...")
        c.save_context()
        t2 = time()

        print("Serializing...")
        serialize_as_n3()
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

    try:
        do_insert(config=options.config, logging=options.do_logging)
    except IOError as e:
        if e.errno == 2 and 'default.conf' in e.filename:
            print("Couldn't find the 'default.conf' configuration file. You may have attempted to run this script in the wrong directory")
