from __future__ import print_function
import PyOpenWorm as P
import traceback
import sqlite3

SQLITE_DB_LOC = '../aux_data/celegans.db'
LINEAGE_LIST_LOC = '../aux_data/C. elegans Cell List - WormAtlas.tsv'

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

def upload_muscles():
    """ Upload muscles and the neurons that connect to them
    """
    try:
        ev = P.Evidence(title="C. elegans sqlite database")
        conn = sqlite3.connect(SQLITE_DB_LOC)
        cur = conn.cursor()
        w = P.Worm()
        cur.execute("""
        SELECT DISTINCT a.Entity, b.Entity
        FROM tblrelationship innervatedBy, tblentity b, tblentity a, tblrelationship type_b
        WHERE innervatedBy.EnID1=a.id and innervatedBy.Relation = '1516' and innervatedBy.EnID2=b.id
        and type_b.EnID1 = b.id and type_b.Relation='1515' and type_b.EnID2='1519'
        """) # 1519 is the
        for r in cur.fetchall():
            neuron_name = str(r[0])
            muscle_name = str(r[1])
            m = P.Muscle(muscle_name)
            n = P.Neuron(neuron_name)
            w.muscle(m)
            m.innervatedBy(n)

        ev.asserts(w)
        ev.save()
        #second step, get the relationships between them and add them to the graph
        print ("uploaded muscles")
    except Exception:
        traceback.print_exc()
    finally:
        conn.close()

def upload_lineage_and_descriptions():
    """ Upload lineage names and descriptions pulled from the WormAtlas master cell list

    Assumes that Neurons and Muscles have already been added
    """
    # XXX: This wants a way to insert cells, then later, to insert neurons from the same set
    # and have the later recoginzed as the former. Identifier matching limits us here. It would
    # be best to establish owl:sameAs links to the super class (Cell) from the subclass (Neuron)
    # at the sub-class insert and have a reasoner relate
    # the two sets of inserts.
    cells = dict()
    try:
        w = P.Worm()
        net = w.neuron_network.one()
        ev = P.Evidence(uri="http://www.wormatlas.org/celllist.htm")
        # insert neurons.
        # save
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

        for n in net.neuron():
            add_data_to_cell(n)

        # TODO: Add data for to other cells here. Requires relating named
        # muscle cells to their counterparts in the cell list: mu_bod(#)
        # Also requires removing neurons and muscles from the list once
        # they've been identified

        ev.asserts(w)
        ev.save()
        print ("uploaded lineage and descriptions")
    except Exception, e:
        traceback.print_exc()

def norn(x):
    """ return the next or None of an iterator """
    try:
        return next(x)
    except StopIteration:
        return None

def upload_neurons():
    try:
        conn = sqlite3.connect(SQLITE_DB_LOC)
        cur = conn.cursor()
        ev = P.Evidence(title="C. elegans sqlite database")
        w = P.Worm()
        n = P.Network()
        w.neuron_network(n)
        # insert neurons.
        # save
        cur.execute("""
        SELECT DISTINCT a.Entity FROM tblrelationship, tblentity a, tblentity b
        where EnID1=a.id and Relation = '1515' and EnID2='1'
        """)
        for r in cur.fetchall():
            neuron_name = str(r[0])
            n.neuron(P.Neuron(name=neuron_name))
        ev.asserts(w)
        ev.save()
        #second step, get the relationships between them and add them to the graph
        print ("uploaded neurons")
    except Exception:
        traceback.print_exc()
    finally:
        conn.close()

def upload_receptors_and_innexins():
    try:
        conn = sqlite3.connect(SQLITE_DB_LOC)
        cur = conn.cursor()
        w = P.Worm()
        n = P.Network()
        w.neuron_network(n)
        # insert neurons.
        # save
        # get the receptor (361), neurotransmitters (354), and innexins (355)
        neurons = dict()

        def add_data_to_neuron(data_kind, relation_code):
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
                if name == "AVAL":
                    print (data)

                if not (name in neurons):
                    neurons[name] = P.Neuron(name=name)

                getattr(neurons[name],data_kind)(data)

        add_data_to_neuron('receptor', 361)
        add_data_to_neuron('innexin', 355)
        add_data_to_neuron('neurotransmitter', 354)

        for neur in neurons:
            n.neuron(neurons[neur])
        n.save()
        #second step, get the relationships between them and add them to the graph
        print ("uploaded receptors and innexins")
    except Exception:
        traceback.print_exc()
    finally:
        conn.close()

def upload_synapses():
    try:
        conn = sqlite3.connect(SQLITE_DB_LOC)
        cur = conn.cursor()
        w = P.Worm()
        n = P.Network()
        w.neuron_network(n)
        #second step, get the relationships between them and add them to the graph
        cur.execute("SELECT DISTINCT a.Entity, b.Entity, Weight, Relation FROM tblrelationship, tblentity a, tblentity b where EnID1=a.id and EnID2=b.id and (Relation = '356' OR Relation = '357')")

        for r in cur.fetchall():
            #all items are numbers -- need to be converted to a string
            first = str(r[0])
            second = str(r[1])
            third = str(r[2])
            syntype = str(r[3])
            if syntype == '356':
                syntype = 'send'
            else:
                syntype = 'gapjunction'
            try:
                weight = int(third)
                # NMJs have negative weights. we only want the synaptic connections
                if weight < 0:
                    syntype = 'gapjunction'
                    weight = -1 * weight

            except:
                weight = None

            if weight:
                c = P.Connection(pre_cell=first, post_cell=second, number=weight, syntype=syntype)
                n.synapse(c)
        e = P.Evidence(author='markw@cs.utexas.edu')
        e.asserts(w)
        e.save()
        print ("uploaded synapses")
    except Exception, e:
        traceback.print_exc()
    finally:
        conn.close()

def upload_types():
    import csv
    ev = P.Evidence(title="neurons.csv")
    w = P.Worm()
    net = w.neuron_network.one()

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

    for n in net.neuron():
        name = n.name.one()
        types = data[name]
        for t in types:
            print("setting type {} for {}.".format(t, name))
            n.type(t)
        w.cell(n)
    ev.asserts(w)
    ev.save()
    print ("uploaded types")

def infer():
    from rdflib import Graph
    from FuXi.Rete.RuleStore import SetupRuleStore
    from FuXi.Rete.Util import generateTokenSet
    from FuXi.Horn.HornRules import HornFromN3

    try:
        w = P.Worm()
        semnet = w.rdf #fetches the entire worm.db graph

        rule_store, rule_graph, network = SetupRuleStore(makeNetwork=True)
        closureDeltaGraph = Graph()
        network.inferredFacts = closureDeltaGraph

        #build a network of rules
        for rule in HornFromN3('testrules.n3'):
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

    except Exception, e:
        traceback.print_exc()
    print ("filled in with inferred data")

def do_insert(config="default.conf", logging=False):
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
        upload_neurons()
        upload_muscles()
        upload_lineage_and_descriptions()
        upload_synapses()
        upload_receptors_and_innexins()
        upload_types()
        #infer()
    except:
        traceback.print_exc()
    finally:
        P.disconnect()

if __name__ == '__main__':
    # Takes about 17 minutes with ZODB FileStorage store
    # Takes about 3 minutes with Sleepycat store
    import sys
    import os
    logging = False
    if len(sys.argv) > 1 and sys.argv[1] == '-l':
        logging = True
    try:
        do_insert(logging=logging)
    except IOError as e:
        if e.errno == 2 and 'default.conf' in e.filename:
            print("Couldn't find the 'default.conf' configuration file. You may have attempted to run this script in the wrong directory")
