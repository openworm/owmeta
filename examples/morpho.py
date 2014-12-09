"""
How to load morphologies of certain cells from the database.
"""
import PyOpenWorm as P

#Create dummy database configuration. Normally you would connect to the actual database.
d = P.Data({
    "rdf.upload_block_statement_count" : 50,
    "user.email" : "jerry@cn.com"
})

#Connect to database with dummy configuration.
P.connect(conf=d)

#Create a new Cell object to work with.
aval = P.Cell(name="AVAL")

#Get the morphology associated with the Cell. Returns a neuroml.Morphology object.
morph = aval.morphology()
print morph

#Disconnect from the database.
P.disconnect()
