import csv
import rdflib
import pprint

# Initialize graph library, only if it was not inited before
if 'g' not in locals() or 'g' not in globals():
    g = rdflib.Graph ("ZODB")

# Will need prefixes to create queries
prefix={'ns1': '<http://openworm.org/entities/Cell/>',
        'ns2': '<http://openworm.org/entities/SimpleProperty/>',
        'ns3': '<http://openworm.org/entities/Muscle/>',
        'ns4': '<http://openworm.org/entities/Neuron/>',
        'ns5': '<http://openworm.org/entities/Evidence/>',
        'ns6': '<http://openworm.org/entities/Network/>',
        'ns7': '<http://openworm.org/entities/Connection/>',
        'ns8': '<http://openworm.org/entities/Worm/>',
        'ns9': '<http://openworm.org/entities/DataObject/>',
        'rdf': '<http://www.w3.org/1999/02/22-rdf-syntax-ns#>',
        'rdfs': '<http://www.w3.org/2000/01/rdf-schema#>',
        'xml': '<http://www.w3.org/XML/1998/namespace>',
        'xsd': '<http://www.w3.org/2001/XMLSchema#>'
        }

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

def return_nodes (query, print_result=False):
    r = g.query(query).result
    print str(len(r)) + " nodes are found"
    if print_result: pprint.pprint(r)
    return r

def get_all_neurons ():
    res = {}
    for n in neurons:
        res[n] = select_nodes_by_name(n).result
    return res

def print_selected_node (id):
    pprint.pprint(select_nodes_by_name(neurons[id]).result)

def prove_unique_neurons (print_temp_result = False):
    """ Repeat the test made to prove that every neuron should has only one appearance in db
    After getting result use: result[neurons[id]], where id is a neuron position in the array. Or use a name of neuron you know
    :return: the dictionary, neuron name is a key, value is an appearance of neurons in the database
    :return: thi dictionary, where appearance is a key and value is an array of the names
    """
    result = {}
    n_result = {}
    appearance = 0
    for n in neurons:
        l = len(select_nodes_by_name(n).result)
        appearance += l
        result[n] = l
        if n_result.has_key(l):
            n_result[l].append (n)
        else:
            n_result[l] = [n]
    if print_temp_result:
        print "Sum of all results is " + str(appearance)
    return result, n_result

#Create dictionary of neurons
n_dic = {}
for n in neurons:
    temp_r = select_nodes_by_name(n).result
    if len(temp_r) > 0:
        name, prop = temp_r[0]
    else: name, prop = '', ''
    n_dic[n] = {'name':name, 'property':prop}

if __name__ == 'main':
    load_worm_data()
    res, res2 = prove_unique_neurons(True)
    print "In the current database neurons appear as following:"
    print res2



