"""
Create a new instance of the database.
The database created will be in this directory (`PyOpenWorm/examples`), and will
be useful for some other examples.
"""
import sys
import PyOpenWorm as P
sys.path.insert(0,'..')

#Connect to a new database using the `default.conf` file.
#The line { "rdf.store_conf" : "worm.db" } in the .conf file means
#the db will be created in the current directory, and called `worm.db`
P.connect('default.conf')

#This operation loads triples from a file and saves them to the database.
#This only has to be performed once, when the database is initially set up.
P.loadData('../OpenWormData/out.n3', 'n3')

#Disconnect from the database for now. We can reconnect later.
P.disconnect()
