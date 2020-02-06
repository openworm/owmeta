"""
How to load morphologies of certain cells from the database.
"""
#this is an expected failure right now, as morphology is not implemented
from __future__ import absolute_import
from __future__ import print_function

from six import StringIO
import owmeta_core as P
from owmeta_core.context import Context

from owmeta.worm import Worm

#Connect to database.
with P.connect('default.conf') as conn:
    ctx = Context(ident="http://openworm.org/data", conf=conn.conf).stored

    #Create a new Cell object to work with.
    aval = ctx(Worm)().get_neuron_network().aneuron('AVAL')

    #Get the morphology associated with the Cell. Returns a neuroml.Morphology object.
    morph = aval._morphology()
    out = StringIO()
    morph.export(out, 0) # we're printing it here, but we would normally do something else with the morphology object.
    print(str(out.read()))
