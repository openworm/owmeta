"""
How to reference supporting evidence for some object in the database.

See: "Metadata in PyOpenWorm" for discussion on semantics of what giving
evidence for an object means.
"""

import sys
import PyOpenWorm as P

#Create dummy database configuration.
d = P.Data({})

#Connect to database with dummy configuration
P.connect(conf=d)

#Create a new Neuron object to work with
n = P.Neuron(name='AVAL')

#Create a new Evidence object with `doi` and `pmid` fields populated.
#See `PyOpenWorm/evidence.py` for other available fields.
e = P.Evidence(doi='125.41.3/ploscompbiol', pmid='57182010')

#Evidence object asserts something about the enclosed dataObject.
#Here we add a receptor to the Neuron we made earlier, and "assert it".
#As the discussion (see top) reads, this might be asserting the existence of
#receptor UNC-8 on neuron AVAL.
e.asserts(n.receptor('UNC-8'))

#Save the Neuron and Evidence objects to the database.
n.save()
e.save()

#What does my evidence object contain?
print e

#Disconnect from the database.
P.disconnect()
