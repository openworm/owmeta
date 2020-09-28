"""Using monoamine-receptor and neuropeptide-receptor mappings published in Bentley et al 2016
(https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1005283)
generate lists of putative extrasynaptic edges as described in that paper.

The resulting network may not be identical to the edge lists presented in the paper,
due potentially to different expression data and ambiguities in neuropeptide/receptor naming.
"""
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

from collections import namedtuple, defaultdict
import csv

from owmeta_core.command import OWM
from owmeta_core import connect
from owmeta_core.context import Context
from owmeta.worm import Worm
import six

#Connect to database.
BASE_URL = (
    "https://raw.githubusercontent.com/clbarnes/bentley_2016_S1_dataset/master/"
    "S1%20Dataset.%20Included%20are%20edge%20lists%20and%20source%20data%20for%20monoamine%20and%20neuropeptide%20networks/"
    "expression_data/"
)

Edge = namedtuple("Edge", ["pre_cell", "post_cell", "transmitter", "receptor"])


def get_mappings():
    """Fetch cells' neurotransmitters, neuropeptides and receptors from owmeta.

    :return: tuple of (
        dict from cell name to set of neurotransmitter and neuropeptide names,
        dict from receptor name to set of cell names
    )
    """
    cell_transmitter_mapping = dict()
    receptor_cell_mapping = defaultdict(set)
    for neuron in net.neurons():
        name = neuron.name.one()
        cell_transmitter_mapping[name] = set(neuron.neuropeptide.get()).union(neuron.neurotransmitter.get())
        for receptor in neuron.receptors.get():
            receptor_cell_mapping[receptor].add(name)

    return cell_transmitter_mapping, receptor_cell_mapping


def get_possible_extrasynaptic_edges(cell_transmitter_mapping, transmitter_receptor_mapping, receptor_cell_mapping):
    """Produce edge lists of potential monoamine and neuropeptide connections unconstrained by physical connectivity.

    :param cell_transmitter_mapping: dict from cell to iterable of transmitters
    :param transmitter_receptor_mapping: dict from transmitter to iterable of receptors
    :param receptor_cell_mapping: dict from receptor to iterable of cells
    :return: iterator of namedtuples of (pre_cell, post_cell, transmitter, receptor)
    """
    for pre_cell, transmitter_set in cell_transmitter_mapping.items():
        for transmitter in transmitter_set:
            for receptor in transmitter_receptor_mapping.get(transmitter, []):
                for post_cell in receptor_cell_mapping.get(receptor, []):
                    yield Edge(pre_cell, post_cell, transmitter, receptor)


def decode_lines(response, encoding='utf-8'):
    for line in response:
        if six.PY2:
            yield line
        else:
            yield line.decode(encoding)


def fetch_np_mapping():
    """Fetch associations between neuropeptides and their receptors from Bentley data.

    :return: dict from neuropeptide gene names (upper case) to cognate receptor gene names (upper case).
    """
    url = BASE_URL + "neuropeptide_receptor_mapping.tsv"
    mapping = defaultdict(set)
    for row in csv.DictReader(decode_lines(urlopen(url)), delimiter='\t'):
        if int(row.get("excluded", 0)):
            continue
        mapping[row["neuropeptide"].upper()].add(row["receptor"].upper())
    return mapping


def fetch_ma_mapping():
    """Fetch associations between monoamines and their receptors from Bentley data.

    :return: dict from full monoamine names (title case) to cognate receptor gene names (upper case).
    """
    url = BASE_URL + "monoamine_receptor_expression.tsv"
    mapping = defaultdict(set)
    for row in csv.DictReader(decode_lines(urlopen(url)), delimiter='\t'):
        if int(row.get("excluded", 0)):
            continue
        mapping[row["monoamine"].title()].add(row["receptor"].upper())
    return mapping


with OWM('../.owm').connect() as conn:
    ctx = conn(Context)(ident="http://openworm.org/data").stored
    #Get the worm object.
    worm = ctx(Worm).query()
    #Extract the network object from the worm object.
    net = worm.neuron_network()

    cell_transmitter_mapping, receptor_cell_mapping = get_mappings()

    ma_t_r_mapping = fetch_ma_mapping()
    ma_edges = list(get_possible_extrasynaptic_edges(cell_transmitter_mapping, ma_t_r_mapping, receptor_cell_mapping))

    np_t_r_mapping = fetch_np_mapping()
    np_edges = list(get_possible_extrasynaptic_edges(cell_transmitter_mapping, np_t_r_mapping, receptor_cell_mapping))

    print('Monamine edges: count={}'.format(len(ma_edges)))
    for x in ma_edges[:4]:
        print(x)
    print('...')
    print()
    print('Neuropeptide edges: count={}'.format(len(np_edges)))
    for x in np_edges[:4]:
        print(x)
    print('...')
