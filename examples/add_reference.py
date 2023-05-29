"""
How to reference supporting evidence for some object in the database.

See: "Metadata in owmeta" for discussion on semantics of what giving
evidence for an object means.
"""

from __future__ import absolute_import
from __future__ import print_function

import owmeta_core as P
from owmeta_core.data import Data
from owmeta_core.dataobject import DataObject
from owmeta_core.context import Context, IMPORTS_CONTEXT_KEY

from owmeta.evidence import Evidence
from owmeta.neuron import Neuron
from owmeta.document import Document

# Create dummy database configuration.
d = Data()
d[IMPORTS_CONTEXT_KEY] = 'http://example.org/imports'

# Connect to database with dummy configuration
conn = P.connect(conf=d)
conn.mapper.add_class(Evidence)
conn.mapper.add_class(Document)
evctx = conn(Context)(ident='http://example.org/meta')
ctx = evctx(Context)(ident='http://example.org/data')

# Add the Context RDF class to the mapper -- normally you'd get these from the
# openworm/owmeta-core bundle as a dependency
conn.mapper.add_class(type(ctx.rdf_object))

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

evctx.add_import(Document.definition_context)
evctx.save_imports()

# Add a couple contexts to the store so we can resolve needed types. normally you'd get
# these from the openworm/owmeta-core bundle as a dependency, so they don't have to be
# added to the database again.
Document.definition_context.save_context(conn.rdf)
DataObject.definition_context.save_context(conn.rdf)

# What does my evidence object contain?
for e_i in evctx.stored(Evidence)().load():
    print(e_i.reference(), e_i.supports())

# Disconnect from the database.
conn.disconnect()
