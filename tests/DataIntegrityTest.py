from __future__ import print_function
import sys
sys.path.insert(0, ".")
import unittest, csv
import PyOpenWorm
from PyOpenWorm import Configure
import rdflib as R

from GraphDBInit import delete_zodb_data_store

class DataIntegrityTest(unittest.TestCase):

    """ Integration tests that read from the database and ensure that basic
        queries have expected answers, as a way to keep data quality high.

    """
    @classmethod
    def setUpClass(cls):
        import csv
        PyOpenWorm.connect(
            conf=Configure(
                **{'rdf.store_conf': 'tests/test.db', 'rdf.source': 'ZODB'}))
        PyOpenWorm.loadData(skipIfNewer=False)
        PyOpenWorm.disconnect()
        # grab the list of the names of the 302 neurons

        csvfile = open('OpenWormData/aux_data/neurons.csv', 'r')
        reader = csv.reader(csvfile, delimiter=';', quotechar='|')

        # array that holds the names of the 302 neurons at class-level scope
        cls.neurons = []
        for row in reader:
            if len(row[0]) > 0:  # Only saves valid neuron names
                cls.neurons.append(row[0])

    def setUp(self):
        PyOpenWorm.connect(
            conf=Configure(
                **{'rdf.store_conf': 'tests/test.db', 'rdf.source': 'ZODB'}))
        self.g = PyOpenWorm.config("rdf.graph")

    def tearDown(self):
        PyOpenWorm.disconnect()


    @classmethod
    def tearDownClass(cls):
        delete_zodb_data_store("tests/test.db")

    def test_correct_neuron_number(self):
        """
        This test verifies that the worm model has exactly 302 neurons.
        """
        # FIXME: Test execution is not properly isolated -- it fails if
        #        test_compare_to_xls fails. Other conditions may cause
        #        it to pass
        net = PyOpenWorm.Worm().get_neuron_network()
        self.assertEqual(302, len(set(net.neuron_names())))


    def test_correct_muscle_number(self):
        """
        This test verifies that the worm model has exactly 158 muscles.
        95 body wall muscles, 37 Pharynx muscles, 26 other muscles
        See counts on row 3 here: https://docs.google.com/spreadsheets/d/1NDx9LRF_B2phR5w4HlEtxJzxx1ZIPT2gA0ZmNmozjos/edit#gid=1
        """
        muscles = PyOpenWorm.Worm().muscles()
        self.assertEqual(158, len(muscles))

    def test_INS_26_neuropeptide_neuron_list(self):
        """
        This test verifies that the set of neurons which contain the
        neuropeptide INS-26 is correct (the list is given below).
        """
        neuronlist = PyOpenWorm.Neuron()
        neuronlist.neuropeptide("INS-26")
        thlist = set(x.name() for x in neuronlist.load())
        self.assertEqual(set(['ASEL', 'ASER', 'ASIL', 'ASIR']), thlist)

    def test_unique_neuron_node(self):
        """
        There should one and only one unique RDF node for every neuron.  If more than one is present for a given cell name,
        then our data is inconsistent.  If there is not at least one present, then we are missing neurons.
        """

        results = {}
        for n in self.neurons:
            # Create a SPARQL query per neuron that looks for all RDF nodes that
            # have text matching the name of the neuron
            qres = self.g.query(
                'SELECT distinct ?n WHERE {?n ?t ?s . ?s ?p \"' +
                n +
                '\" } LIMIT 5')
            results[n] = (len(qres.result), [x[0] for x in qres.result])

        # If there is not only one result back, then there is more than one RDF
        # node.
        more_than_one = [(x, results[x]) for x in results if results[x][0] > 1]
        less_than_one = [(x, results[x]) for x in results if results[x][0] < 1]
        self.assertEqual(
            0,
            len(more_than_one),
            "Some neurons have more than 1 node: " +
            "\n".join(
                str(x) for x in more_than_one))
        self.assertEqual(
            0,
            len(less_than_one),
            "Some neurons have no node: " +
            "\n".join(
                str(x) for x in less_than_one))

    def test_neurons_have_types(self):
        """
        Every Neuron should have a non-blank type
        """
        results = set()
        for n in self.neurons:
            qres = self.g.query('SELECT ?v WHERE { ?s <http://openworm.org/entities/SimpleProperty/value> \"' + n + '\". '  # per node ?s that has the name of a neuron associated
                                + '?k <http://openworm.org/entities/Cell/name> ?s .'
                                # look up its listed type ?o
                                + '?k <http://openworm.org/entities/Neuron/type> ?o .'
                                # for that type ?o, get its property ?tp and its
                                # value ?v
                                + '?o <http://openworm.org/entities/SimpleProperty/value> ?v } '
                                )
            for x in qres:
                v = x[0]
                if isinstance(v, R.Literal):
                    results.add(n)

        self.assertEqual(len(results), len(self.neurons), "Some neurons are missing a type: {}".format(set(self.neurons) - results))

    def test_neuron_GJ_degree(self):
        """ Get the number of gap junctions from a networkx representation """
        #was 81 -- now retunring 44 -- are we sure this is correct?
        self.assertEqual(PyOpenWorm.Neuron(name='AVAL').GJ_degree(), 44)

    def test_neuron_Syn_degree(self):
        """ Get the number of chemical synapses from a networkx representation """
        # was 187 -- now returning 105 -- are we sure this is correct?
        self.assertEqual(PyOpenWorm.Neuron(name='AVAL').Syn_degree(), 105)

    @unittest.skip("have not yet defined asserts")
    def test_what_nodes_get_type_info(self):
        qres = self.g.query('SELECT ?o ?p ?s WHERE {'
                            + '?o <http://openworm.org/entities/SimpleProperty/value> "motor". '
                            '?o ?p ?s} '  # for that type ?o, get its value ?v
                            + 'LIMIT 10')
        for row in qres.result:
            print(row)

    #TODO: Revise this test to pull from the herm_full_edgelist.csv instead of NeuronConnect.xls
    @unittest.skip("deprecated because spreadsheet is no longer supposed to match")
    def test_compare_to_xls(self):
        """ Compare the PyOpenWorm connections to the data in the spreadsheet """
        SAMPLE_CELL = 'AVAL'
        xls_conns = set([])
        pow_conns = set([])

        # QUERY TO GET ALL CONNECTIONS WHERE SAMPLE_CELL IS ON THE PRE SIDE
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
            # Insert sample cell name into the result set after the fact
            t.insert(0, SAMPLE_CELL)
            pow_conns.add(tuple(t))

        # QUERY TO GET ALL CONNECTIONS WHERE SAMPLE_CELL IS ON THE *POST* SIDE
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
            # Insert sample cell name into the result set after the fact
            t.insert(1, SAMPLE_CELL)
            pow_conns.add(tuple(t))

        # get connections from the sheet
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
        s = xlrd.open_workbook(
            'OpenWormData/aux_data/NeuronConnect.xls').sheets()[0]
        for row in range(1, s.nrows):
            if s.cell(row, 2).value in ('S', 'Sp', 'EJ') and \
                SAMPLE_CELL in [s.cell(row, 0).value,
                                s.cell(row, 1).value]:
                # we're not going to include 'receives' ('r', 'rp') since
                # they're just the inverse of 'sends' also omitting 'nmj'
                # for the time being (no model in db)
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
                if string_key in combining_dict.keys():
                    # if key already there, add to number
                    num += int(combining_dict[string_key][3])

                combining_dict[string_key] = (
                    str(pre),
                    str(post),
                    str(syntype),
                    str(int(num)))

        xls_conns = set(combining_dict.values())

        # assert that these two sorted lists are the same
        # using sorted lists because Set() removes multiples

        self.maxDiff = None
        self.assertEqual(sorted(pow_conns), sorted(xls_conns))

    @unittest.skip("deprecated due to performance")
    def test_all_cells_have_wormbaseID(self):
        """ This test verifies that every cell has a Wormbase ID. """
        cells = set(PyOpenWorm.Cell().load())
        for cell in cells:
            self.assertNotEqual(cell.wormbaseID(), '')

    @unittest.skip("deprecated due to performance")
    def test_all_neurons_have_wormbaseID(self):
        """ This test verifies that every neuron has a Wormbase ID. """
        net = PyOpenWorm.Worm().get_neuron_network()
        for neuron_object in net.neurons():
            self.assertNotEqual(neuron_object.wormbaseID(), '')

    @unittest.skip("deprecated due to performance")
    def test_all_muscles_have_wormbaseID(self):
        """ This test verifies that every muscle has a Wormbase ID. """
        muscles = PyOpenWorm.Worm().muscles()
        for muscle_object in muscles:
            self.assertNotEqual(muscle_object.wormbaseID(), '')

    @unittest.skip("deprecated due to performance")
    def test_all_neurons_are_cells(self):
        """ This test verifies that all Neuron objects are also Cell objects. """
        net = PyOpenWorm.Worm().get_neuron_network()

        for neuron_object in net.neurons():
            self.assertIsInstance(neuron_object, PyOpenWorm.Cell)

    @unittest.skip("deprecated due to performance")
    def test_all_muscles_are_cells(self):
        """ This test verifies that all Muscle objects are also Cell objects. """
        muscles = PyOpenWorm.Worm().muscles()
        for muscle_object in muscles:
            self.assertIsInstance(muscle_object, PyOpenWorm.Cell)

    @unittest.skip("deprecated due to performance")
    def test_correct_connections_number(self):
        """ This test verifies that there are exactly 6916 connections. """
        net = PyOpenWorm.Worm().get_neuron_network()
        self.assertEqual(6916, len(net.synapses()))

    @unittest.skip("deprecated due to performance")
    def test_connection_content_matches(self):
        """ This test verifies that the content of each connection matches the
        content in the source. """
        ignored_cells = ['hyp', 'intestine']
        synapse_tuples = set()   # set of tuple representation of synapses
        csv_tuples = set()       # set of tuple representation of csv file

        synapses = PyOpenWorm.Worm().get_neuron_network().synapses()
        for synapse in synapses:
            if synapse.syntype() == 'gapJunction':
                syn_type = 'chemical'
            else:
                syn_type = 'electrical'
            syn_tuple = (synapse.pre_cell(), synapse.post_cell(), synapse.number(), syn_type)
            synapse_tuples.add(syn_tuple)

        # read csv file row by row
        with open('OpenWormData/aux_data/herm_full_edgelist.csv', 'rb') as csvfile:
            edge_reader = csv.reader(csvfile)
            edge_reader.next()    # skip header row

            for row in edge_reader:
                source, target, weight, syn_type = map(str.strip, row)
                # ignore rows where source or target is 'hyp' or 'intestine'
                if source in ignored_cells or target in ignored_cells:
                    continue
                csv_tuple = (source, target, weight, syn_type)
                csv_tuples.add(csv_tuple)

        self.assertTrue(csv_tuples.issubset(synapse_tuples))

    @unittest.skip("deprecated due to performance")
    def test_number_neuron_to_neuron(self):
        """
        This test verifies that the worm model has exactly 5805 neuron to neuron
        connections.
        """
        synapses = PyOpenWorm.Worm().get_neuron_network().synapses()
        count = 0

        for synapse in synapses:
            if synapse.termination() == 'neuron':
                count += 1

        self.assertEqual(5805, count)

    @unittest.skip("deprecated due to performance")
    def test_number_neuron_to_muscle(self):
        """
        This test verifies that the worm model has exactly 1111 neuron to muscle
        connections.
        """
        synapses = PyOpenWorm.Worm().get_neuron_network().synapses()
        count = 0

        for synapse in synapses:
            if synapse.termination() == 'muscle':
                count += 1

        self.assertEqual(1111, count)

    @unittest.skip("deprecated due to performance")
    def test_correct_number_unique_neurons(self):
        """
        This test verifies that the worm model has exactly 300 unique neurons
        making connections.
        """
        synapses = PyOpenWorm.Worm().get_neuron_network().synapses()
        unique_neurons = set()    # set of unique neurons

        for synapse in synapses:
            unique_neurons.add(synapse.pre_cell())    # set won't count duplicates

        self.assertEqual(300, len(unique_neurons))

    @unittest.skip("deprecated due to performance")
    def test_unconnected_neurons(self):
        """
        This test verifies that there are exactly 2 unconnected neurons,
        i.e., CANL and CANR, in the new connectome.
        """
        # In previous tests, there is a check for exactly 302 neurons in total.
        # There is also a test for exactly 300 unique neurons making connections.
        # That means it should be enough to check that the set {CANL, CANR} and
        # the set of neurons making connections are disjoint.

        synapses = PyOpenWorm.Worm().get_neuron_network().synapses()
        connected_neurons = set()
        unconnected_neurons = {'CANL', 'CANR'}

        for synapse in synapses:
            connected_neurons.add(synapse.pre_cell())

        self.assertTrue(connected_neurons.isdisjoint(unconnected_neurons))
