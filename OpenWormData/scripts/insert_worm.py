from __future__ import print_function
import PyOpenWorm as P
import traceback
import csv
import sqlite3
import re

SQLITE_DB_LOC = '../aux_data/celegans.db'
LINEAGE_LIST_LOC = '../aux_data/C. elegans Cell List - WormAtlas.tsv'
CELL_NAMES_SOURCE = "../aux_data/C. elegans Cell List - WormBase.csv"
CONNECTOME_SOURCE = "../aux_data/herm_full_edgelist.csv"


def serialize_as_n3():
    dest = '../WormData.n3'
    # XXX: Properties aren't initialized until the first object of a class is created,
    #      so we create them here

    for x in dir(P):
        if isinstance(getattr(P, x), type) and issubclass(getattr(P, x), P.DataObject):
            c = getattr(P, x)
            if x == 'values':
                c("dummy")
            else:
                c()
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


# to normalize certain neuron names
search_string = re.compile(r'\w+[0]+[1-9]+')
replace_string = re.compile(r'[0]+')


def normalize(name):
    # normalize neuron names to match those used at other points
    # see #137 for elaboration
    # if there are zeroes in the middle of a name, remove them
    if re.match(search_string, name):
        name = replace_string.sub('', name)
    return name

def upload_muscles():
    """ Upload muscles and the neurons that connect to them
    """
    try:
        with open(CELL_NAMES_SOURCE) as csvfile:
            csvreader = csv.reader(csvfile)

            ev = P.Evidence(title="C. elegans Cell List - WormBase.csv")
            w = P.Worm()
            for num, line in enumerate(csvreader):
                if num < 4:  # skip rows with no data
                    continue

                if line[7] or line[8] or line[9] == '1':  # muscle's marked in these columns
                    muscle_name = normalize(line[0]).upper()
                    m = P.Muscle(name=muscle_name)
                    w.muscle(m)
            ev.asserts(w)
            ev.save()
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

        # TODO: Add data for other cells here. Requires relating named
        # muscle cells to their counterparts in the cell list (e.g. mu_bod(#))
        # Also requires removing neurons and muscles from the list once
        # they've been identified so they aren't stored twice

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
        ev = P.Evidence(title="C. elegans Cell List - WormBase.csv")
        w = P.Worm()
        n = P.Network()
        w.neuron_network(n)
        # insert neurons.
        # save
        with open(CELL_NAMES_SOURCE) as csvfile:
            csvreader = csv.reader(csvfile)

            for num, line in enumerate(csvreader):
                if num < 4:  # skip rows with no data
                    continue

                if line[5] == '1':  # neurons marked in this column
                    neuron_name = normalize(line[0]).upper()
                    n.neuron(P.Neuron(name=neuron_name))

        ev.asserts(n)
        ev.save()
        #second step, get the relationships between them and add them to the graph
        print ("uploaded neurons")
    except Exception:
        traceback.print_exc()


def upload_receptors_and_innexins():
    try:
        conn = sqlite3.connect(SQLITE_DB_LOC)
        cur = conn.cursor()
        w = P.Worm()
        n = w.neuron_network()
        # insert neurons.
        # save
        # get the receptor (361), neurotransmitters (313), neuropeptides (354) and innexins (355)
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

                if not (name in neurons):
                    neurons[name] = P.Neuron(name=name)

                getattr(neurons[name],data_kind)(data)

        add_data_to_neuron('receptor', 361)
        add_data_to_neuron('innexin', 355)
        add_data_to_neuron('neurotransmitter', 313)
        add_data_to_neuron('neuropeptide', 354)

        for neur in neurons:
            n.neuron(neurons[neur])
        n.save()
        #second step, get the relationships between them and add them to the graph
        print ("uploaded receptors, innexins, neurotransmitters and neuropeptides")
    except Exception:
        traceback.print_exc()
    finally:
        conn.close()


def upload_connections():

    # to normalize certian body wall muscle cell names
    search_string_muscle = re.compile(r'\w+[BWM]+\w+')
    replace_string_muscle = re.compile(r'[BWM]+')

    def normalize_muscle(name):
        # normalize names of Body Wall Muscles
        # if there is 'BWM' in the name, remove it
        if re.match(search_string_muscle, name):
            name = replace_string_muscle.sub('', name)
        return name

    # connectome specific definitions

    # cells that are generically definited in source. These will not be added to PyOpenWorm
    unwanted = ['HYP', 'INTESTINE']

    # muscle cells that are generically defined in source and need to be broken into pair of L and R before being added to PyOpenWorm
    to_expand_muscles = ['PM1D', 'PM2D', 'PM3D', 'PM4D', 'PM5D']

    # muscle cells that have different names in connectome source and cell list. Their wormbase cell list names will be used in PyOpenWorm
    changed_muscles = ['ANAL', 'INTR', 'INTL', 'SPH']

    def changed_muscle(x):
        return {
            'ANAL': 'MU_ANAL',
            'INTR': 'MU_INT_R',
            'INTL': 'MU_INT_L',
            'SPH': 'MU_SPH'
        }[x]

    # cells that are neither neurons or muscles. These are marked as 'Other Cells' in the wormbase cell list but are still part of the new connectome. In future work these should be uploaded seperately to PyOpenWorm in a new upload function and should be referred from there instead of this list.
    other_cells = ['MC1DL', 'MC1DR', 'MC1V', 'MC2DL', 'MC2DR', 'MC2V', 'MC3DL', 'MC3DR','MC3V']

    # counters for terminal printing
    neuron_connections = 0
    muscle_connections = 0
    other_connections = 0
    unwanted_connections = 0

    try:
        w = P.Worm()
        n = P.Network()
        neuron_objs = list(set(n.neurons()))
        muscle_objs = list(w.muscles())
        w.neuron_network(n)

        # get lists of neuron and muscles names
        neurons = [neuron.name() for neuron in neuron_objs]
        muscles = [muscle.name() for muscle in muscle_objs]

        # Evidence object to assert each connection
        e = P.Evidence(uri='herm_full_edgelist.csv')

        with open(CONNECTOME_SOURCE) as csvfile:
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
                source = normalize(source).upper()
                target = normalize(target).upper()

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

                # if the source cell is a neuron
                if source in neurons:
                    if target in neurons:
                        c = P.Connection(
                                        pre_cell=source, post_cell=target,
                                        number=weight, syntype=syn_type,
                                        termination='neuron'
                                        )
                        n.synapse(c)
                        e.asserts(c)
                        neuron_connections += 1
                        continue

                    elif target in muscles:
                        c = P.Connection(
                                        pre_cell=source, post_cell=target,
                                        number=weight, syntype=syn_type,
                                        termination='muscle'
                                        )
                        n.synapse(c)
                        e.asserts(c)
                        muscle_connections += 1
                        continue

                    elif target in to_expand_muscles:
                        target_L = target+'L'
                        target_R = target+'R'
                        c1 = P.Connection(
                                        pre_cell=source, post_cell=target_L,
                                        number=weight, syntype=syn_type,
                                        termination='muscle'
                                        )
                        c2 = P.Connection(
                                        pre_cell=source, post_cell=target_R,
                                        number=weight, syntype=syn_type,
                                        termination='muscle'
                                        )
                        n.synapse(c1)
                        n.synapse(c2)
                        e.asserts(c1)
                        e.asserts(c2)
                        muscle_connections += 2
                        continue

                    elif target in other_cells:
                        c = P.Connection(
                                        pre_cell=source, post_cell=target,
                                        number=weight, syntype=syn_type,
                                        )
                        n.synapse(c)
                        e.asserts(c)
                        other_connections += 1
                        continue

                    else:
                        unwanted_connections += 1
                        continue

                # if the source cell is a muscle
                if source in muscles:
                    if target in neurons:
                        c = P.Connection(
                                        pre_cell=source, post_cell=target,
                                        number=weight, syntype=syn_type,
                                        termination='muscle'
                                        )
                        n.synapse(c)
                        e.asserts(c)
                        muscle_connections += 1
                        continue

                    elif target in muscles:
                        c = P.Connection(
                                        pre_cell=source, post_cell=target,
                                        number=weight, syntype=syn_type,
                                        )
                        n.synapse(c)
                        e.asserts(c)
                        other_connections += 1
                        continue

                    elif target in to_expand_muscles:
                        target_L = target+'L'
                        target_R = target+'R'
                        c1 = P.Connection(
                                        pre_cell=source, post_cell=target_L,
                                        number=weight, syntype=syn_type
                                        )
                        c2 = P.Connection(
                                        pre_cell=source, post_cell=target_R,
                                        number=weight, syntype=syn_type
                                        )
                        n.synapse(c1)
                        n.synapse(c2)
                        e.asserts(c1)
                        e.asserts(c2)
                        other_connections += 2
                        continue

                    elif target in other_cells:
                        c = P.Connection(
                                        pre_cell=source, post_cell=target,
                                        number=weight, syntype=syn_type,
                                        )
                        n.synapse(c)
                        e.asserts(c)
                        other_connections += 1
                        continue

                    else:
                        unwanted_connections += 1
                        continue

                # if the source cell is one of the to_expand_muscles
                if source in to_expand_muscles:
                    source_L = source + 'L'
                    source_R = source + 'R'

                    if target in neurons:
                        c1 = P.Connection(
                                        pre_cell=source_L, post_cell=target,
                                        number=weight, syntype=syn_type,
                                        termination='muscle'
                                        )
                        c2 = P.Connection(
                                        pre_cell=source_R, post_cell=target,
                                        number=weight, syntype=syn_type,
                                        termination='muscle'
                                        )
                        n.synapse(c1)
                        n.synapse(c2)
                        e.asserts(c1)
                        e.asserts(c2)
                        muscle_connections += 2
                        continue

                    elif target in muscles:
                        c1 = P.Connection(
                                        pre_cell=source_L, post_cell=target,
                                        number=weight, syntype=syn_type
                                        )
                        c2 = P.Connection(
                                        pre_cell=source_R, post_cell=target,
                                        number=weight, syntype=syn_type
                                        )
                        n.synapse(c1)
                        n.synapse(c2)
                        e.asserts(c1)
                        e.asserts(c2)
                        other_connections += 2
                        continue

                    elif target in to_expand_muscles:
                        target_L = target + 'L'
                        target_R = target + 'R'
                        c1 = P.Connection(
                                        pre_cell=source_L, post_cell=target_L,
                                        number=weight, syntype=syn_type
                                        )
                        c2 = P.Connection(
                                        pre_cell=source_R, post_cell=target_L,
                                        number=weight, syntype=syn_type
                                        )
                        c3 = P.Connection(
                                        pre_cell=source_L, post_cell=target_R,
                                        number=weight, syntype=syn_type
                                        )
                        c4 = P.Connection(
                                        pre_cell=source_R, post_cell=target_R,
                                        number=weight, syntype=syn_type
                                        )
                        n.synapse(c1)
                        n.synapse(c2)
                        n.synapse(c3)
                        n.synapse(c4)
                        e.asserts(c1)
                        e.asserts(c2)
                        e.asserts(c3)
                        e.asserts(c4)
                        other_connections += 4
                        continue

                    elif target in other_cells:
                        c1 = P.Connection(
                                        pre_cell=source_L, post_cell=target,
                                        number=weight, syntype=syn_type
                                        )
                        c2 = P.Connection(
                                        pre_cell=source_R, post_cell=target,
                                        number=weight, syntype=syn_type
                                        )
                        n.synapse(c1)
                        n.synapse(c2)
                        e.asserts(c1)
                        e.asserts(c2)
                        other_connections += 2
                        continue

                    else:
                        unwanted_connections += 1
                        continue

                # if the source cell is in other_cells
                if source in other_cells:
                    if target in to_expand_muscles:
                        target_L = target+'L'
                        target_R = target+'R'
                        c1 = P.Connection(
                                        pre_cell=source, post_cell=target_L,
                                        number=weight, syntype=syn_type
                                        )
                        c2 = P.Connection(
                                        pre_cell=source, post_cell=target_R,
                                        number=weight, syntype=syn_type
                                        )
                        n.synapse(c1)
                        n.synapse(c2)
                        e.asserts(c1)
                        e.asserts(c2)
                        other_connections += 2
                        continue

                    elif target in unwanted:
                        unwanted_connections += 1
                        continue

                    else:
                        c = P.Connection(
                                        pre_cell=source, post_cell=target,
                                        number=weight, syntype=syn_type,
                                        )
                        n.synapse(c)
                        e.asserts(c)
                        other_connections += 1
                        continue

                # if the source was neither a neuron nor muscle nor other_cell
                unwanted_connections += 1

        e.asserts(n)  # assert the whole connectome too
        e.save()
        print('Total neuron to neuron connections added = %i' %neuron_connections)
        print('Total neuron to muscle connections added = %i' %muscle_connections)
        print('Total other connections added = %i' %other_connections)
        print('Total connections discarded = %i' %unwanted_connections)
        print('uploaded connections')

    except Exception, e:
        traceback.print_exc()


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

    for name in data:
        n = P.Neuron(name=name)
        types = data[name]
        for t in types:
            n.type(t)
        net.neuron(n)
    ev.asserts(net)
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
        w = P.Worm()
        net = P.Network()
        w.neuron_network(net)
        w.save()

        upload_neurons()
        upload_muscles()
        upload_lineage_and_descriptions()
        upload_connections()
        upload_receptors_and_innexins()
        upload_types()
        serialize_as_n3()
        #infer()
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
    import os
    logging = False
    if len(sys.argv) > 1 and sys.argv[1] == '-l':
        logging = True
    try:
        do_insert(logging=logging)
    except IOError as e:
        if e.errno == 2 and 'default.conf' in e.filename:
            print("Couldn't find the 'default.conf' configuration file. You may have attempted to run this script in the wrong directory")
