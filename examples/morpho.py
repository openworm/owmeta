"""
How to load morphologies of certain cells from the database.
"""
#this is an expected failure right now, as morphology is not implemented
from __future__ import absolute_import
from __future__ import print_function
import PyOpenWorm as P
from PyOpenWorm.context import Context
from PyOpenWorm.worm import Worm
from OpenWormData import BIO_ENT_NS

from six import StringIO

#Connect to database.
conn = P.connect('default.conf')

ctx = Context(ident=BIO_ENT_NS['worm0'], conf=conn).stored

#Create a new Cell object to work with.
aval = ctx(Worm)().get_neuron_network().aneuron('AVAL')

#Get the morphology associated with the Cell. Returns a neuroml.Morphology object.
morph = aval._morphology()
out = StringIO()
morph.export(out, 0) # we're printing it here, but we would normally do something else with the morphology object.
print(str(out.read()))

#Disconnect from the database.
P.disconnect(conn)
