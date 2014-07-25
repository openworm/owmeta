import PyOpenWorm as P
import traceback
import sqlite3
def print_evidence():
    try:
        conn = sqlite3.connect('db/celegans.db')
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT a.Entity, b.Entity, Citations FROM tblrelationship, tblentity a, tblentity b where EnID1=a.id and EnID2=b.id and Citations!='' ")
        for r in cur.fetchall():
            print r
    except Exception:
        traceback.print_exc()
    finally:
        conn.close()

def upload_muscles():
    try:
        conn = sqlite3.connect('db/celegans.db')
        cur = conn.cursor()
        w = P.Worm()
        # insert neurons.
        # save
        cur.execute("SELECT DISTINCT b.Entity FROM tblrelationship, tblentity b where Relation = '1516' and EnID2=b.id")
        for r in cur.fetchall():
            muscle_name = str(r[0])
            w.muscle(P.Muscle(muscle_name))
        w.save()
        #second step, get the relationships between them and add them to the graph
    except Exception:
        traceback.print_exc()
    finally:
        conn.close()

def upload_neurons():
    try:
        conn = sqlite3.connect('db/celegans.db')
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
        conn = sqlite3.connect('db/celegans.db')
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
        conn = sqlite3.connect('db/celegans.db')
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

if __name__ == '__main__':
    d = P.Data({
        "connectomecsv" : "https://raw.github.com/openworm/data-viz/master/HivePlots/connectome.csv",
        "neuronscsv" : "https://raw.github.com/openworm/data-viz/master/HivePlots/neurons.csv",
        "sqldb" : "/home/markw/work/openworm/PyOpenWorm/db/celegans.db",
        "rdf.source"  : "sparql_endpoint",
        "rdf.store"  : "SPARQLUpdateStore",
        "rdf.store_conf"  : ["http://107.170.133.175:8080/openrdf-sesame/repositories/test","http://107.170.133.175:8080/openrdf-sesame/repositories/test/statements"],
        "rdf.upload_block_statement_count" : 1000,
        "user.email" : "jerry@cn.com",
        "test_variable" : "test_value"
    })
    import sys
    logging = False
    if len(sys.argv) > 1 and sys.argv[1] == '-l':
        logging = True
    P.connect(configFile='readme.conf',do_logging=logging)
    try:
        #print_evidence()
        upload_muscles()
        #upload_synapses()
        #upload_receptors_and_innexins()
    except:
        pass
    #try:
        #for x in P.Neuron().load():
            #print x
        ##q = """
            ##prefix openworm: <http://openworm.org/entities/>
            ##prefix neuron: <http://openworm.org/entities/Neuron/>
            ##prefix sp: <http://openworm.org/entities/SimpleProperty/>
            ##select distinct ?Neuron where
            ##{
                ##?Neuron_name sp:value "AVAL" .
                ##?Neuron neuron:name ?Neuron_name .
                ##?Neuron_name rdf:type openworm:Neuron_name .

                ##?Neuron rdf:type openworm:Neuron .
            ##}
            ##"""
        ##for x in P.Configureable.default['rdf.graph'].query(q):
            ##print x
    #except:
        #traceback.print_exc()
    P.disconnect()

