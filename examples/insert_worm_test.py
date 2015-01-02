"""This test goes through insert_worm script and trying to repeat what it is doing, but by my way (Anton)
Generally, we would like to end up with Notation3 file, representing every triples we need for the Worm working
Note: All pathways are formed from the main directory
"""
import sqlite3

CELEGANS_DATABASE = 'OpenWormData/aux_data/celegans.db'

# Let's first upload all neurons from the db
def upload_neurons ():
    neuron_names = []
    try:
        conn = sqlite3.connect(CELEGANS_DATABASE)
        cur = conn.cursor()

        # Get all names from db
        cur.execute("""
            SELECT DISTINCT a.Entity
            FROM tblrelationship, tblentity a, tblentity b
            where EnID1=a.id
            and Relation = '1515' # is a
            and EnID2='1'
            """)

        # Stack all names
        for r in cur.fetchall():
            name = str(r[0])
            neuron_names.append(name)
        return neuron_names

    except Exception:
        pass
    finally:
        conn.close()


# Lets create the new db-n3 and load step by step there facts
