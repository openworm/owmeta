import csv
import rdflib
import pprint

# Initialize graph library, only if it was not inited before
if 'g' not in locals() or 'g' not in globals():
    g = rdflib.Graph ("ZODB")

def load_worm_data ():
    g.parse("OpenWormData/WormData.n3", format='n3')

# Load all names of neurons
neurons = []
csvfile = open('OpenWormData/aux_data/neurons.csv', 'r')
reader = csv.reader(csvfile, delimiter=';', quotechar='|')
for row in reader:
    if len(row[0]) > 0: # Only saves valid neuron names
      neurons.append(row[0])

def select_nodes_by_name (name):
    this_query = 'SELECT ?name ?property WHERE {?name ?property \"'+ name + '\" } LIMIT 5 '
    return g.query(this_query)

def print_selected_node (id):
    pprint.pprint(select_nodes_by_name(neurons[id]).result)

def prove_unique_neurons ():
    """ Repeat the test made to prove that every neuron should has only one appearance in db
    After getting result use: result[neurons[id]], where id is a neuron position in the array. Or use a name of neuron you know
    :return: the dictionary with appearance of neurons in the database
    """
    result = {}
    for n in neurons:
        result[n] = len(select_nodes_by_name(n).result)
    return result


