import PyOpenWorm as P
import traceback
import sqlite3

def print_evidence():
    try:
        conn = sqlite3.connect('celegans.db')
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT a.Entity, b.Entity, Citations FROM tblrelationship, tblentity a, tblentity b where EnID1=a.id and EnID2=b.id and Citations!='' ")
        for r in cur.fetchall():
            print r
    except Exception:
        traceback.print_exc()
    finally:
        conn.close()

def upload_muscles():
    """ Upload muscles and the neurons that connect to them
    """
    try:
        conn = sqlite3.connect('celegans.db')
        cur = conn.cursor()
        w = P.Worm()
        cur.execute("SELECT DISTINCT a.Entity, b.Entity FROM tblrelationship, tblentity b, tblentity a where Relation = '1516' and EnID2=b.id and EnID1=a.id")
        for r in cur.fetchall():
            muscle_name = str(r[1])
            m = P.Muscle(muscle_name)
            w.muscle(m)
            n = P.Neuron(str(r[0]))
            m.innervatedBy(n)

        w.save()
        #second step, get the relationships between them and add them to the graph
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
        ev = P.Evidence(uri="http://www.wormatlas.org/celllist.htm")
        # insert neurons.
        # save
        f = open("C. elegans Cell List - WormAtlas.tsv", "r")
        h = open("C. elegans Cell List - WormBase.tsv", "r")

        # Skip headers
        next(h)
        next(h)
        next(h)
        next(f)
        names = dict()
        for x in f:
             j = [x.strip().strip("\"") for x in x.split("\t")]
             name=j[0]
             if name in names:
                 while (name in names):
                     names[name] += 1
                     name = name + "("+ str(names[name]) +")"
             else:
                 names[name] = 0

             c = P.Cell(name,j[1])
             c.description(j[2])
             w.cell(c)
             cells[name] = (j[1],j[2])
        # We bring in the neurons and muscles through their shared name
        # -- the name is the only thing that relates these sets of
        # objects

        ev.asserts(w)
        ev.save()
    except Exception, e:
        traceback.print_exc()
    return cells

def norn(x):
    """ return the next or None of an iterator """
    try:
        return next(x)
    except StopIteration:
        return None

def update_neurons_and_muscles_with_lineage_and_descriptions():
    v = P.values('neurons and muscles')
    #XXX: This could be expensive...the lineage name and description should be loaded with the cell though.
    cells = {next(x.name()) : (norn(x.lineageName()), norn(x.description())) for x in P.Cell().load() }
    def dtt(x):
        """ Do the thing """
        try:
            name = next(x.name())
            if cells[name][0] is not None:
                x.lineageName(cells[name][0])
            if cells[name][1] is not None:
                x.description(cells[name][1])
            v.value(x)
        except:
            traceback.print_exc()
    for x in P.Neuron().load():
        dtt(x)
    for x in P.Muscle().load():
        dtt(x)

    v.save()

def upload_neurons():
    try:
        conn = sqlite3.connect('celegans.db')
        cur = conn.cursor()
        w = P.Worm()
        n = P.Network()
        w.neuron_network(n)
        # insert neurons.
        # save
        cur.execute("SELECT DISTINCT a.Entity FROM tblrelationship, tblentity a, tblentity b where EnID1=a.id and Relation = '1515' and EnID2='1'")
        for r in cur.fetchall():
            neuron_name = str(r[0])
            n.neuron(P.Neuron(name=neuron_name))
        n.save()
        #second step, get the relationships between them and add them to the graph
    except Exception:
        traceback.print_exc()
    finally:
        conn.close()

def upload_receptors_and_innexins():
    try:
        conn = sqlite3.connect('celegans.db')
        cur = conn.cursor()
        w = P.Worm()
        n = P.Network()
        w.neuron_network(n)
        # insert neurons.
        # save
        # get the receptor (354) and innexin (355)
        cur.execute("""
        SELECT DISTINCT a.Entity, b.Entity
        FROM
        tblrelationship q,
        tblrelationship r,
        tblentity a,
        tblentity b
        where q.EnID1=a.id and q.Relation = '1515' and q.EnID2='1'
        and   r.EnID1=a.id and r.Relation = '354'  and r.EnID2=b.id
        """)
        for r in cur.fetchall():
            neuron_name = str(r[0])
            receptor = str(r[1])
            neur = P.Neuron(name=neuron_name)
            neur.receptor(receptor)
            n.neuron(neur)
        cur.execute("""
        SELECT DISTINCT a.Entity, b.Entity
        FROM
        tblrelationship q,
        tblrelationship r,
        tblentity a,
        tblentity b
        where q.EnID1=a.id and q.Relation = '1515' and q.EnID2='1'
        and   r.EnID1=a.id and r.Relation = '355'  and r.EnID2=b.id
        """)
        for r in cur.fetchall():
            neuron_name = str(r[0])
            innexin = str(r[1])
            neur = P.Neuron(name=neuron_name)
            neur.innexin(innexin)
            n.neuron(neur)
        n.save()
        #second step, get the relationships between them and add them to the graph
    except Exception:
        traceback.print_exc()
    finally:
        conn.close()

def upload_synapses():
    try:
        conn = sqlite3.connect('celegans.db')
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
    except Exception, e:
        traceback.print_exc()
    finally:
        conn.close()

def do_insert():
    import sys
    logging = False
    if len(sys.argv) > 1 and sys.argv[1] == '-l':
        logging = True
    P.connect(configFile='default.conf',do_logging=logging)
    try:
        upload_muscles()
        print ("uploaded muscles")
        upload_lineage_and_descriptions()
        print ("uploaded lineage and descriptions")
        upload_synapses()
        print ("uploaded synapses")
        upload_receptors_and_innexins()
        print ("uploaded receptors and innexins")
        update_neurons_and_muscles_with_lineage_and_descriptions()
        print ("updated muscles and neurons with cell data")
    except:
        traceback.print_exc()
    finally:
        P.disconnect()

if __name__ == '__main__':
    do_insert()
