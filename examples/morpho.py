"""
How to load morphologies of certain cells from the database.
"""
#this is an expected failure right now, as morphology is not implemented
import PyOpenWorm as P

#Connect to database.
P.connect()

#Create a new Cell object to work with.
aval = P.Worm().get_neuron_network().aneuron('AVAL')

#Get the morphology associated with the Cell. Returns a neuroml.Morphology object.
morph = aval.morphology()
print morph #we're printing it here, but we would normally do something else with the morphology object.

#Disconnect from the database.
P.disconnect()
