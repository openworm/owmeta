import re
import traceback
import csv

from ..utils import normalize_cell_name
from ..connection import Connection
from ..cell import Cell
from ..evidence import Evidence
from ..neuron import Neuron
from ..muscle import Muscle

from .csv_ds import CSVDataTranslator, CSVDataSource
from .common_data import TRANS_NS
from .data_with_evidence_ds import DataWithEvidenceDataSource


class ConnectomeCSVDataSource(CSVDataSource):
    pass


class NeuronConnectomeCSVTranslator(CSVDataTranslator):
    input_type = ConnectomeCSVDataSource
    output_type = DataWithEvidenceDataSource
    translator_identifier = TRANS_NS.NeuronConnectomeCSVTranslator

    def translate(data_source):

        print ("uploading statements about connections")

        # muscle cells that are generically defined in source and need to be broken
        # into pair of L and R before being added to PyOpenWorm
        to_expand_muscles = ['PM1D', 'PM2D', 'PM3D', 'PM4D', 'PM5D']

        # muscle cells that have different names in connectome source and cell list.
        # Their wormbase cell list names will be used in PyOpenWorm
        changed_muscles = ['ANAL', 'INTR', 'INTL', 'SPH']

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

            with open(data_source.csv_file_name.onedef()) as csvfile:
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


# to normalize certian body wall muscle cell names
SEARCH_STRING_MUSCLE = re.compile(r'\w+[BWM]+\w+')
REPLACE_STRING_MUSCLE = re.compile(r'[BWM]+')


def normalize_muscle(name):
    # normalize names of Body Wall Muscles
    # if there is 'BWM' in the name, remove it
    if re.match(SEARCH_STRING_MUSCLE, name):
        name = REPLACE_STRING_MUSCLE.sub('', name)
    return name

def changed_muscle(x):
    return {
        'ANAL': 'MU_ANAL',
        'INTR': 'MU_INT_R',
        'INTL': 'MU_INT_L',
        'SPH': 'MU_SPH'
    }[x]

def expand_muscle(name):
    return Muscle(name + 'L'), Muscle(name + 'R')

__yarom_mapped_classes__ = (ConnectomeCSVDataSource, NeuronConnectomeCSVTranslator)
