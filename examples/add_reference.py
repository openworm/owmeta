"""
How to reference supporting evidence for some object in the database.

See: "Metadata in PyOpenWorm" for discussion on semantics of what giving
evidence for an object means.
"""

from __future__ import absolute_import
from __future__ import print_function
import PyOpenWorm as P
from PyOpenWorm.evidence import Evidence
from PyOpenWorm.neuron import Neuron
from PyOpenWorm.document import Document
from PyOpenWorm.data import Data
from PyOpenWorm.context import Context

# Create dummy database configuration.
d = Data({'rdf.source': 'ZODB'})

# Connect to database with dummy configuration
P.connect(conf=d)

ctx = Context(ident='http://example.org/data')
evctx = Context(ident='http://example.org/meta')

print(id(P.config('rdf.graph')))
print(P.config('rdf.graph'))
print(evctx.stored.rdf_graph().serialize(format='n3').decode('utf-8'))
# Create a new Neuron object to work with
n = ctx(Neuron)(name='AVAL')

# Create a new Evidence object with `doi` and `pmid` fields populated.
# See `PyOpenWorm/evidence.py` for other available fields.
d = evctx(Document)(key='Anonymous2011', doi='125.41.3/ploscompbiol', pmid='12345678')
e = evctx(Evidence)(key='Anonymous2011', reference=d)

# Evidence object asserts something about the enclosed dataObject.
# Here we add a receptor to the Neuron we made earlier, and "assert it".
# As the discussion (see top) reads, this might be asserting the existence of
# receptor UNC-8 on neuron AVAL.
n.receptor('UNC-8')

e.supports(ctx.rdf_object)

print(id(ctx.conf['rdf.graph']))
# Save the Neuron and Evidence objects to the database.
ctx.save_context()
evctx.save_context()

print(1)
print(evctx.stored.rdf_graph().serialize(format='nquads').decode('utf-8'))

print(2)
print(evctx.conf['rdf.graph'].serialize(format='nquads').decode('utf-8'))

# What does my evidence object contain?
for e_i in evctx.stored(Evidence)().load():
    print(e_i.reference())
    print(e_i.supports())

# Disconnect from the database.
P.disconnect()
