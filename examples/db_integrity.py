"""
This script helps to look into the database, and its integrity.
It loads database, and then sort neurons to the dictionary.
Dictionary structure so far:
[neuron_name]
            [name] - subject of the node with neuron_name as object
            [neuron] - subject of the neuron in the main node

"""
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
    if len(g) > 1000:
        print ("Database has been already loaded")
        return
    print ("Parse worm database into python...")
    g.parse("OpenWormData/WormData.n3", format='n3')
    print ("Done!")

# Load all names of neurons
neurons = []
csvfile = open('OpenWormData/aux_data/neurons.csv', 'r')
reader = csv.reader(csvfile, delimiter=';', quotechar='|')
for row in reader:
    if len(row[0]) > 0: # Only saves valid neuron names
        # There are two neurons with * sign. We don't want them to be in neuron name
        star = row[0].find('*')
        n_name = row[0]
        if star > -1:
            n_name = n_name[0:star]
        neurons.append(n_name)

def select_nodes_neuron (name):
    this_query = 'SELECT ?name ?cell WHERE {?name ?sp \"' + name + '\". ' \
                                        '?cell <http://openworm.org/entities/Cell/name> ?name. ' \
                                        '?cell a <http://openworm.org/entities/Neuron>}'
    return g.query(this_query)

def return_nodes (query, print_result=False):
    r = g.query(query).result
    if print_result:
        pprint.pprint(r)
        print str(len(r)) + " nodes are found"
    return r

def get_all_neurons ():
    res = {}
    for n in neurons:
        res[n] = select_nodes_neuron(n).result
    return res

def print_selected_node (id):
    pprint.pprint(select_nodes_neuron(neurons[id]).result)

def get_all_nodes_by_name (print_temp_result = False):
    """ Repeat the test made to prove that every neuron should has only one appearance in db
    After getting result use: result[neurons[id]], where id is a neuron position in the array. Or use a name of neuron you know
    :return: the dictionary, neuron name is a key, value is an appearance of neurons in the database
    :return: thi dictionary, where appearance is a key and value is an array of the names
    """
    result = {}
    n_result = {}
    appearance = 0
    for n in neurons:
        qres = g.query('SELECT ?s ?p WHERE {?s ?p \"' + n + '\" }')
        l = len(qres.result)
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
# n_dic[neuron_name] -> ['name'] = hash address of the name property;
#                       ['neuron'] = hash address of this neuron, connected to the worm
def combine_data_to_dic ():
    n_dic = {}
    print ("Take all neurons from db and sort them into dictionary..")
    for n in neurons:
        temp_r = select_nodes_neuron(n).result
        #0 index is neuron_name, 1 is neuron
        if len(temp_r) > 0:
            name, neuron = temp_r[0]
        else: name, neuron = '', ''
        n_dic[n] = {'name':name, 'neuron':neuron}
    print ("Done")
    return n_dic

load_worm_data()
if 'n_dic' not in locals() or 'n_dic' not in globals():
    n_dic = combine_data_to_dic()

def get_prove ():
    prove1, prove2 = get_all_nodes_by_name()
    print ("In the current database each neuron has the following amount of nodes")
    for p in prove2:
        print (prove2[p])

def check_types ():
    ntype_query = "SELECT ?type ?value WHERE {?type a <http://openworm.org/entities/Neuron_type>. " \
                  "?type <http://openworm.org/entities/SimpleProperty/value> ?value}"
    return g.query(ntype_query).result

def get_neurons_with_types ():
    type_neurons_query = "SELECT ?name_value ?type_value WHERE {?type a <http://openworm.org/entities/Neuron_type>." \
                  "?type <http://openworm.org/entities/SimpleProperty/value> ?type_value." \
                  "?cell <http://openworm.org/entities/Neuron/type> ?type." \
                  "?cell <http://openworm.org/entities/Cell/name> ?name." \
                  "?name <http://openworm.org/entities/SimpleProperty/value> ?name_value." \
                  "?name a <http://openworm.org/entities/Cell_name>}"
    return g.query(type_neurons_query).result



