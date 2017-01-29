"""
How to load morphologies of certain cells from the database.
"""
#this is an expected failure right now, as morphology is not implemented
from __future__ import absolute_import
from __future__ import print_function
import PyOpenWorm as P
import cStringIO as io

#Connect to database.
P.connect('default.conf')

#Create a new Cell object to work with.
aval = P.Worm().get_neuron_network().aneuron('AVAL')

#Get the morphology associated with the Cell. Returns a neuroml.Morphology object.
morph = aval._morphology()
out = io.StringIO()
morph.export(out, 0) #we're printing it here, but we would normally do something else with the morphology object.
print(str(out.read()))

#Disconnect from the database.
P.disconnect()
