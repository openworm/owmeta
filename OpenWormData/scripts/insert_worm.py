from __future__ import print_function
import PyOpenWorm as P
import traceback
import sqlite3
import re
import xlrd
import csv

SQLITE_DB_LOC = '../aux_data/celegans.db'
LINEAGE_LIST_LOC = '../aux_data/C. elegans Cell List - WormAtlas.tsv'
SQLITE_EVIDENCE = None
WORM = None
NETWORK = None

OPTIONS = None

def serialize_as_n3():
    dest = '../WormData.n3'
    # XXX: Properties aren't initialized until the first object of a class is created,
    #      so we create them here

    P.config('rdf.graph').serialize(dest, format='n3')
    print('serialized to n3 file')


def print_evidence():
    try:
        conn = sqlite3.connect(SQLITE_DB_LOC)
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT a.Entity, b.Entity, Citations FROM tblrelationship, tblentity a, tblentity b where EnID1=a.id and EnID2=b.id and Citations!='' ")
        for r in cur.fetchall():
            print(r)
    except Exception:
        traceback.print_exc()
    finally:
        conn.close()

def add_muscles():
    """ Upload muscles and the neurons that connect to them
    """
    try:
        conn = sqlite3.connect(SQLITE_DB_LOC)
        cur = conn.cursor()
        w = WORM
        cur.execute("""
        SELECT DISTINCT a.Entity, b.Entity
        FROM tblrelationship innervatedBy, tblentity b, tblentity a, tblrelationship type_b
        WHERE innervatedBy.EnID1=a.id and innervatedBy.Relation = '1516' and innervatedBy.EnID2=b.id
        and type_b.EnID1 = b.id and type_b.Relation='1515' and type_b.EnID2='1519'
        """) # 1519 is the
        for r in cur.fetchall():
            neuron_name = str(r[0])
            muscle_name = str(r[1])
            m = P.Muscle(key=muscle_name, name=muscle_name)
            n = P.Neuron(name=neuron_name)
            w.muscle(m)
            m.innervatedBy(n)

        SQLITE_EVIDENCE.asserts(w)
        print ("uploaded muscles")
    except Exception:
        traceback.print_exc()
    finally:
        conn.close()

def add_lineage_and_descriptions():
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

             # XXX: These renaming choices are arbitrary and may be inappropriate
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
                     name = name + "("+ str(cell_name_counters[name]) +")"
             else:
                 cell_name_counters[name] = 0

             data[name] = {"lineageName" : lineageName, "desc": desc}

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

def add_neurons():
    try:
        conn = sqlite3.connect(SQLITE_DB_LOC)
        cur = conn.cursor()
        n = NETWORK

        cur.execute("""
        SELECT DISTINCT a.Entity FROM tblrelationship, tblentity a, tblentity b
        where EnID1=a.id and Relation = '1515' and EnID2='1'
        """)
        neuron_count = 0
        for r in cur.fetchall():
            neuron_name = str(r[0])
            n.neuron(P.Neuron(name=neuron_name))
            neuron_count += 1
        SQLITE_EVIDENCE.asserts(n)
        #second step, get the relationships between them and add them to the graph
        print("uploaded neurons")
    except Exception:
        traceback.print_exc()
    finally:
        conn.close()

def add_receptors_and_innexins():
    try:
        conn = sqlite3.connect(SQLITE_DB_LOC)
        cur = conn.cursor()
        n = NETWORK
        # get the receptor (361), neurotransmitters (313), neuropeptides (354) and innexins (355)
        neurons = dict()

        def add_data_to_neuron(data_kind, relation_code):
            print("Adding", data_kind, "data")
            cur.execute("""
                SELECT DISTINCT a.Entity, b.Entity
                FROM
                tblrelationship q,
                tblrelationship r,
                tblentity a,
                tblentity b
                where q.EnID1=a.id and q.Relation = '1515' and q.EnID2='1'
                and   r.EnID1=a.id and r.Relation = '{}'  and r.EnID2=b.id
                """.format(relation_code))
            for r in cur.fetchall():
                name = str(r[0])
                data = str(r[1])

                if name not in neurons:
                    neurons[name] = P.Neuron(name=name)

                getattr(neurons[name], data_kind)(data)
            print("Added", data_kind, "data")

        add_data_to_neuron('receptor', 361)
        add_data_to_neuron('innexin', 355)
        add_data_to_neuron('neurotransmitter', 313)
        add_data_to_neuron('neuropeptide', 354)

        for neur in neurons:
            n.neuron(neurons[neur])
        #second step, get the relationships between them and add them to the graph
        print ("uploaded receptors, innexins, neurotransmitters and neuropeptides")
        sys.stdout.flush()
    except Exception:
        traceback.print_exc()
    finally:
        conn.close()

def new_connections():
    """we can replace the old function, add_connections, with this
    once it is ready to go"""

    search_string = re.compile(r'\w+[0]+[1-9]+')
    replace_string = re.compile(r'[0]+')

    def normalize(name):
        # normalize neuron names to match those used at other points
        # see #137 for elaboration
        # if there are zeroes in the middle of a name, remove them
        if re.match(search_string, name):
            name = replace_string.sub('', name)
        return name


    try:
        n = NETWORK
        neurons = set(n.neuron_names())

        # Evidence object to assert each connection
        e  = P.Evidence(uri='http://www.wormwiring.org')

        with open('../aux_data/herm_full_edgelist.csv', 'rb') as csvfile:
            edge_reader = csv.reader(csvfile)
            edge_reader.next()    # skip header row
            for row in edge_reader:
                source, target, weight, syn_type = map(str.strip, row)

                # set synapse type to something the Connection object
                # expects, and normalize the source and target names
                if syn_type == 'electrical':
                    syn_type = 'gapJunction'
                elif syn_type == 'chemical':
                    syn_type = 'send'
                source = normalize(source)
                target = normalize(target)
                if source in neurons and target in neurons:
                    c = P.connection(
                        pre_cell=source, post_cell=target,
                        number=weight, syntype=syn_type
                    )

                    n.synapse(c)
                    e.asserts(c)

        e.asserts(n) # assert the whole connectome too
        print('uploaded connections')

    except Exception:
        traceback.print_exc()


def add_connections():
    search_string = re.compile(r'\w+[0]+[1-9]+')
    replace_string = re.compile(r'[0]+')

    def normalize(name):
        # normalize neuron names to match those used at other points
        # see #137 for elaboration
        # if there are zeroes in the middle of a name, remove them
        if re.match(search_string, name):
            name = replace_string.sub('', name)
        return name

    try:
        n = NETWORK
        combining_dict = {}
        # Get synapses and gap junctions and add them to the graph
        s = xlrd.open_workbook('../aux_data/NeuronConnect.xls').sheets()[0]
        for row in range(1, s.nrows):
            if s.cell(row, 2).value in ('S', 'Sp', 'EJ'):
                #We're not going to include 'receives' ('R', 'Rp') since they're just the inverse of 'sends'
                #Also omitting 'NMJ' for the time being (no model in db)
                pre = normalize(s.cell(row, 0).value)
                post = normalize(s.cell(row, 1).value)
                num = int(s.cell(row, 3).value)
                if s.cell(row, 2).value == 'EJ':
                    syntype = 'gapJunction'
                elif s.cell(row, 2).value in ('S', 'Sp'):
                    syntype = 'send'

                # Add them to a dict to make sure Sends ('S') and Send-polys ('Sp') are summed.
                # keying by connection pairs as a string (e.g. 'SDQL,AVAL,send').
                # values are lists of the form [pre, post, number, syntype].
                string_key = '{},{},{}'.format(pre, post, syntype)
                if string_key in combining_dict.keys():
                    # if key already there, add to number
                    combining_dict[string_key][2] += num
                else:
                    combining_dict[string_key] = [pre, post, num, syntype]
        i = 0
        for entry in combining_dict:
            pre, post, num, syntype = combining_dict[entry]
            c = P.Connection(pre_cell=pre, post_cell=post, number=num, syntype=syntype)
            n.synapse(c)
            i += 1
        e = P.Evidence(uri='http://www.wormatlas.org/neuronalwiring.html#Connectivitydata')
        e.asserts(n)
        print('uploaded connections')
    except Exception:
        traceback.print_exc()

def add_types():
    ev = P.Evidence(title="neurons.csv")
    net = NETWORK

    data = dict()
    for x in csv.reader(open('../aux_data/neurons.csv'), delimiter=';'):
        types = []
        name = x[0]
        types_string = x[1]
        if 'sensory' in (types_string.lower()):
            types.append('sensory')
        if 'interneuron' in (types_string.lower()):
            types.append('interneuron')
        if 'motor' in (types_string.lower()):
            types.append('motor')
        data[name] = types

    for name in data:
        n = P.Neuron(name=name)
        types = data[name]
        for t in types:
            n.type(t)
        net.neuron(n)
    ev.asserts(net)
    print ("uploaded types")

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
    global SQLITE_EVIDENCE
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
    SQLITE_EVIDENCE = P.Evidence(key="C_elegans_SQLite_DB", title="C. elegans sqlite database")
    try:
        WORM = P.Worm()
        NETWORK = P.Network()
        WORM.neuron_network(NETWORK)
        NETWORK.worm(WORM)

        add_neurons()
        add_muscles()
        add_lineage_and_descriptions()
        add_connections()
        add_receptors_and_innexins()
        add_types()

        print("Saving...")
        WORM.save()
        infer()

        print("Serializing...")
        serialize_as_n3()
    except:
        traceback.print_exc()
    finally:
        P.disconnect()

if __name__ == '__main__':
    # NOTE: This process will NOT clear out the database if run multiple times.
    #       Multiple runs will add the data again and again.
    # Takes about 5 minutes with ZODB FileStorage store
    # Takes about 3 minutes with Sleepycat store

    import sys
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-l", "--do-logging", dest="do_logging",
                      action="store_true", default=False,
                      help="Enable log output")

    (options, _) = parser.parse_args()
    OPTIONS = options

    try:
        do_insert(logging=options.do_logging)
    except IOError as e:
        if e.errno == 2 and 'default.conf' in e.filename:
            print("Couldn't find the 'default.conf' configuration file. You may have attempted to run this script in the wrong directory")
