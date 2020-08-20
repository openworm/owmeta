"""
How to reference supporting evidence for some object in the database.

See: "Metadata in owmeta" for discussion on semantics of what giving
evidence for an object means.
"""

from __future__ import absolute_import
from __future__ import print_function

import owmeta_core as P
from owmeta_core.data import Data
from owmeta_core.context import Context

from owmeta.evidence import Evidence
from owmeta.neuron import Neuron
from owmeta.document import Document

# Create dummy database configuration.
d = Data()

# Connect to database with dummy configuration
conn = P.connect(conf=d)
conn.mapper.add_class(Evidence)
conn.mapper.add_class(Document)
ctx = conn(Context)(ident='http://example.org/data')
evctx = conn(Context)(ident='http://example.org/meta')

# Create a new Neuron object to work with
n = ctx(Neuron)(name='AVAL')

# Create a new Evidence object with `doi` and `pmid` fields populated.
# See `owmeta/evidence.py` for other available fields.
d = evctx(Document)(key='Anonymous2011', doi='125.41.3/ploscompbiol', pmid='12345678')
e = evctx(Evidence)(key='Anonymous2011', reference=d)

# Evidence object asserts something about the enclosed dataobject.
# Here we add a receptor to the Neuron we made earlier, and "assert it".
# As the discussion (see top) reads, this might be asserting the existence of
# receptor UNC-8 on neuron AVAL.
n.receptor('UNC-8')

e.supports(ctx.rdf_object)

# Save the Neuron and Evidence objects to the database.
ctx.save_context()
evctx.save_context()

# What does my evidence object contain?
for e_i in evctx.stored(Evidence)().load():
    print(e_i.reference(), e_i.supports())

# Disconnect from the database.
P.disconnect(conn)
