from __future__ import absolute_import
from __future__ import print_function
import sys
from six.moves import map
from six.moves import range
sys.path.insert(0,".")
import unittest
import PyOpenWorm
from PyOpenWorm import *
import rdflib
import rdflib as R
import os


USE_BINARY_DB = False
BINARY_DB = "OpenWormData/worm.db"
TEST_CONFIG = "tests/default_test.conf"

namespaces = { "rdf" : "http://www.w3.org/1999/02/22-rdf-syntax-ns#" }

def clear_graph(graph):
    graph.update("CLEAR ALL")

def make_graph(size=100):
    """ Make an rdflib graph """
    g = R.Graph()
    for i in range(size):
        s = rdflib.URIRef("http://somehost.com/s"+str(i))
        p = rdflib.URIRef("http://somehost.com/p"+str(i))
        o = rdflib.URIRef("http://somehost.com/o"+str(i))
        g.add((s,p,o))
    return g

def delete_zodb_data_store(path):
    os.unlink(path)
    os.unlink(path + '.index')
    os.unlink(path + '.tmp')
    os.unlink(path + '.lock')

class DataIntegrityTest(unittest.TestCase):
    """ Integration tests that read from the database and ensure that basic
        queries have expected answers, as a way to keep data quality high.

    """
    @classmethod
    def setUpClass(cls):
        import csv

        cls.neurons = [] #array that holds the names of the 302 neurons at class-level scope

        if not USE_BINARY_DB:
            PyOpenWorm.connect(conf=Data()) # Connect for integrity tests that use PyOpenWorm functions
            cls.g = PyOpenWorm.config('rdf.graph') # declare class-level scope for the database
            cls.g.parse("OpenWormData/WormData.n3", format="n3") # load in the database
        else:
            conf = Configure(**{ "rdf.source" : "ZODB", "rdf.store_conf" : BINARY_DB })
            PyOpenWorm.connect(conf=conf)
            cls.g = PyOpenWorm.config('rdf.graph')

        #grab the list of the names of the 302 neurons

        csvfile = open('OpenWormData/aux_data/neurons.csv', 'r')
        reader = csv.reader(csvfile, delimiter=';', quotechar='|')

        for row in reader:
            if len(row[0]) > 0: # Only saves valid neuron names
                cls.neurons.append(row[0])
    @classmethod
    def tearDownClass(cls):
        PyOpenWorm.disconnect()

    def test_correct_neuron_number(self):
        """
        This test verifies that the worm model has exactly 302 neurons.
        """
        net = PyOpenWorm.Worm().get_neuron_network()
        self.assertEqual(302, len(set(net.neurons())))

    def test_TH_neuropeptide_neuron_list(self):
        """
        This test verifies that the set of neurons which contain the
        neuropeptide TH is correct (the list is given below).
        """
        neuronlist = PyOpenWorm.Neuron()
        neuronlist.neuropeptide("TH")
        thlist = set(x.name() for x in neuronlist.load())
        self.assertEqual(set(['CEPDR', 'PDER', 'CEPDL', 'PDEL', 'CEPVR', 'CEPVL']), thlist)

    def testUniqueNeuronNode(self):
        """
        There should one and only one unique RDF node for every neuron.  If more than one is present for a given cell name,
        then our data is inconsistent.  If there is not at least one present, then we are missing neurons.
        """

        results = {}
        for n in self.neurons:
            #Create a SPARQL query per neuron that looks for all RDF nodes that have text matching the name of the neuron
            qres = self.g.query('SELECT distinct ?n WHERE {?n ?t ?s . ?s ?p \"' + n + '\" } LIMIT 5')
            results[n] = (len(qres.result), [x[0] for x in qres.result])

        # If there is not only one result back, then there is more than one RDF node.
        more_than_one = [(x, results[x]) for x in results if results[x][0] > 1]
        less_than_one = [(x, results[x]) for x in results if results[x][0] < 1]
        self.assertEqual(0, len(more_than_one), "Some neurons have more than 1 node: " + "\n".join(str(x) for x in more_than_one))
        self.assertEqual(0, len(less_than_one), "Some neurons have no node: " + "\n".join(str(x) for x in less_than_one))

    def testNeuronsHaveTypes(self):
        """
        Every Neuron should have a non-blank type
        """
        results = set()
        for n in self.neurons:
            qres = self.g.query('SELECT ?v WHERE { ?s <http://openworm.org/entities/SimpleProperty/value> \"' + n + '\". ' #per node ?s that has the name of a neuron associated
                                + '?k <http://openworm.org/entities/Cell/name> ?s .'
                                + '?k <http://openworm.org/entities/Neuron/type> ?o .' #look up its listed type ?o
                                + '?o <http://openworm.org/entities/SimpleProperty/value> ?v } ' #for that type ?o, get its property ?tp and its value ?v
                                )
            for x in qres:
                v = x[0]
                if isinstance(v,R.Literal):
                    results.add(n)

        # NOTE: Neurons ALNL, CANL, CANR, ALNR have unknown function and type
        self.assertEqual(len(results), len(self.neurons) - 4, "Some neurons are missing a type: {}".format(set(self.neurons) - results))

    def test_neuron_GJ_degree(self):
        """ Get the number of gap junctions from a networkx representation """
        self.assertEqual(PyOpenWorm.Neuron(name='AVAL').GJ_degree(), 40)

    def test_neuron_Syn_degree(self):
        """ Get the number of chemical synapses from a networkx representation """
        self.assertEqual(PyOpenWorm.Neuron(name='AVAL').Syn_degree(), 90)

    @unittest.skip("have not yet defined asserts")
    def testWhatNodesGetTypeInfo(self):
        qres = self.g.query('SELECT ?o ?p ?s WHERE {'
                                + '?o <http://openworm.org/entities/SimpleProperty/value> "motor". '
                                  '?o ?p ?s} ' #for that type ?o, get its value ?v
                                + 'LIMIT 10')
        for row in qres.result:
            print(row)

    def test_compare_to_xls(self):
        """ Compare the PyOpenWorm connections to the data in the spreadsheet """
        SAMPLE_CELL = 'AVAL'
        xls_conns = []
        pow_conns = []

        #QUERY TO GET ALL CONNECTIONS WHERE SAMPLE_CELL IS ON THE PRE SIDE
        qres = self.g.query("""SELECT ?post_name ?type (STR(?num) AS ?numval) WHERE {
                               #############################################################
                               # Find connections that have the ?pre_name as our passed in value
                               #############################################################
                               ?pre_namenode <http://openworm.org/entities/SimpleProperty/value> \'"""
                               + SAMPLE_CELL +
                               """\'.
                               ?pre_cell <http://openworm.org/entities/Cell/name> ?pre_namenode.
                               ?pre <http://openworm.org/entities/SimpleProperty/value> ?pre_cell.
                               ?conn <http://openworm.org/entities/Connection/pre_cell> ?pre.

                               #############################################################
                               # Find all the cells that are on the post side of those
                               #  connections and bind their names to ?post_name
                               #############################################################
                               ?conn <http://openworm.org/entities/Connection/post_cell> ?post.
                               ?post <http://openworm.org/entities/SimpleProperty/value> ?post_cell.
                               ?post_cell <http://openworm.org/entities/Cell/name> ?post_namenode.
                               ?post_namenode <http://openworm.org/entities/SimpleProperty/value> ?post_name.

                               ############################################################
                               # Go find the type of the connection and bind to ?type
                               #############################################################
                               ?conn <http://openworm.org/entities/Connection/syntype> ?syntype_node.
                               ?syntype_node <http://openworm.org/entities/SimpleProperty/value> ?type.

                               ############################################################
                               # Go find the number of the connection and bind to ?num
                               ############################################################
                               ?conn <http://openworm.org/entities/Connection/number> ?number_node.
                               ?number_node <http://openworm.org/entities/SimpleProperty/value> ?num.

                               ############################################################
                               # Filter out any ?pre_names or ?post_names that aren't literals
                               ############################################################
                               FILTER(isLiteral(?post_name))}""")
        def ff(x):
            return str(x.value)
        for line in qres.result:
            t = list(map(ff, line))
            t.insert(0,SAMPLE_CELL) #Insert sample cell name into the result set after the fact
            pow_conns.append(t)

        #QUERY TO GET ALL CONNECTIONS WHERE SAMPLE_CELL IS ON THE *POST* SIDE
        qres = self.g.query("""SELECT ?pre_name ?type (STR(?num) AS ?numval) WHERE {
                               #############################################################
                               # Find connections that have the ?post_name as our passed in value
                               #############################################################
                               ?post_namenode <http://openworm.org/entities/SimpleProperty/value> \'"""
                               + SAMPLE_CELL +
                               """\'.
                               ?post_cell <http://openworm.org/entities/Cell/name> ?post_namenode.
                               ?post <http://openworm.org/entities/SimpleProperty/value> ?post_cell.
                               ?conn <http://openworm.org/entities/Connection/post_cell> ?post.

                               #############################################################
                               # Find all the cells that are on the pre side of those
                               #  connections and bind their names to ?pre_name
                               #############################################################
                               ?conn <http://openworm.org/entities/Connection/pre_cell> ?pre.
                               ?pre <http://openworm.org/entities/SimpleProperty/value> ?pre_cell.
                               ?pre_cell <http://openworm.org/entities/Cell/name> ?pre_namenode.
                               ?pre_namenode <http://openworm.org/entities/SimpleProperty/value> ?pre_name.

                               ############################################################
                               # Go find the type of the connection and bind to ?type
                               #############################################################
                               ?conn <http://openworm.org/entities/Connection/syntype> ?syntype_node.
                               ?syntype_node <http://openworm.org/entities/SimpleProperty/value> ?type.

                               ############################################################
                               # Go find the number of the connection and bind to ?num
                               ############################################################
                               ?conn <http://openworm.org/entities/Connection/number> ?number_node.
                               ?number_node <http://openworm.org/entities/SimpleProperty/value> ?num.

                               ############################################################
                               # Filter out any ?pre_names or ?post_names that aren't literals
                               ############################################################
                               FILTER(isLiteral(?pre_name))}""")
        for line in qres.result:
            t = list(map(ff, line))
            t.insert(1,SAMPLE_CELL) #Insert sample cell name into the result set after the fact
            pow_conns.append(t)

        #get connections from the sheet
        import re
        search_string = re.compile(r'\w+[0]+[1-9]+')
        replace_string = re.compile(r'[0]+')

        def normalize(name):
            # normalize neuron names to match those used at other points
            # see #137 for elaboration
            # if there are zeroes in the middle of a name, remove them
            if re.match(search_string, name):
                name = replace_string.sub('', name)
            return name

        import xlrd
        combining_dict = {}
        # 's' is the workbook sheet
        s = xlrd.open_workbook('OpenWormData/aux_data/NeuronConnect.xls').sheets()[0]
        for row in range(1, s.nrows):
            if s.cell(row, 2).value in ('S', 'Sp', 'EJ') and SAMPLE_CELL in [s.cell(row, 0).value, s.cell(row, 1).value]:
                #we're not going to include 'receives' ('r', 'rp') since they're just the inverse of 'sends'
                #also omitting 'nmj' for the time being (no model in db)
                pre = normalize(s.cell(row, 0).value)
                post = normalize(s.cell(row, 1).value)
                num = int(s.cell(row, 3).value)
                if s.cell(row, 2).value == 'EJ':
                    syntype = 'gapJunction'
                elif s.cell(row, 2).value in ('S', 'Sp'):
                    syntype = 'send'

                # add them to a dict to make sure sends ('s') and send-polys ('sp') are summed.
                # keying by connection pairs as a string (e.g. 'sdql,aval,send').
                # values are lists if the form [pre, post, number, syntype].
                string_key = '{},{},{}'.format(pre, post, syntype)
                if string_key in list(combining_dict.keys()):
                    # if key already there, add to number
                    num += int(combining_dict[string_key][3])

                combining_dict[string_key] = [str(pre), str(post), str(syntype), str(int(num))]


        xls_conns = list(combining_dict.values())

        #assert that these two sorted lists are the same
        #using sorted lists because Set() removes multiples

        self.maxDiff = None
        self.assertEqual(sorted(pow_conns), sorted(xls_conns))
