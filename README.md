[![Build Status](https://travis-ci.org/openworm/PyOpenWorm.png?branch=master)](https://travis-ci.org/openworm/PyOpenWorm/builds)
[![Docs](https://readthedocs.org/projects/pyopenworm/badge/?version=latest)](https://pyopenworm.readthedocs.org/en/latest)
[![Join the chat at https://gitter.im/openworm/pyopenworm](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/openworm/pyopenworm?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge) [![Stories in Ready](https://badge.waffle.io/openworm/pyopenworm.png?label=ready&title=Ready)](https://waffle.io/openworm/pyopenworm)  [![Coverage Status](https://coveralls.io/repos/openworm/PyOpenWorm/badge.svg?branch=dev&service=github)](https://coveralls.io/github/openworm/PyOpenWorm?branch=dev)  [![Code Climate](https://codeclimate.com/github/openworm/PyOpenWorm/badges/gpa.svg)](https://codeclimate.com/github/openworm/PyOpenWorm)

PyOpenWorm
===========

A data access layer in Python which integrates disparate structures
and representations for *C. elegans* anatomy and physiology.  Provides a
clean, high-level interface used by the rest of
[OpenWorm](http://www.openworm.org).  

Overview
--------
The data and models required to simulate *C. elegans* are highly heterogenous.
Consequently, from a software perspective, a variety of underlying
representations are needed to store different aspects
of the relevant anatomy and physiology.  For example,
a NetworkX representation of the connectome as a complex graph enables
questions to be asked about nearest neighbors of a given neuron.
An RDF semantic graph representation is useful for reading and
writing annotations about multiple aspects of a neuron, such as what papers
have been written about it, properties it may have such as
ion channels and neurotransmitter receptors, etc.  A NeuroML representation is useful
for answering questions about model morphology and simulation parameters.  A
Blender representation is a full 3D shape definition that can be used for
calculations in 3D space.

The diversity of underlying representations required for OpenWorm
presents a challenge for data integration and consolidation.  PyOpenWorm solves
this challenge with a unified data access layer whereby different representations
are encapsulated into an abstract view.  This allows the user to work with
objects related to the *biological reality of the worm*, and
forget about which representation is being used under the hood.  The worm
itself has a unified sense of neurons, networks, muscles,
ion channels, etc and so should our code.

Syntactical constructs in PyOpenWorm reflect the structure of
the corresponding biological knowledge-base
rather than the programming domain of the underlying technologies. Wherever possible,
pure Python libraries or those with few compilation requirements are used.

Relationship to ChannelWorm
-----------------------------
[ChannelWorm](https://github.com/openworm/ChannelWorm) is
the sub-project of OpenWorm which houses ion channel models.  In the future,
we expect ChannelWorm to be a "consumer" of PyOpenWorm.  A PyOpenWorm database will house
physical models, the digitized plots they are derived from (there is a Plot type in PyOpenWorm),
and provide code to put those models into enumerated formats along with auxillary
files or comments.  However, because these projects were not developed sequentially,
there is currently some overlap in functionality, and PyOpenWorm itself houses
a fairly substantial amount of physiological information about *C. elegans.*
Ultimately, the pure core of PyOpenWorm, which is a meant to be a data framework
for storing metadata and provenance (i.e. parameters and trajectories
associated with simulations), will be separated out into standalone functionality.  

Versioning data as code
-----------------------

A library that attempts to reliably expose dynamic data can often be broken because
the underlying data sets that define it change over time.  This is because data
changes can cause queries to return different answers than before, causing
unpredictable behavior.  

As such, to create a stable foundational library for others to reuse, the version
of the PyOpenWorm library guarantees the user a specific version of the data
behind that library.  In addition, unit tests are used to ensure basic sanity
checks on data are maintained.  As data are improved, the maintainers of the
library can perform appropriate regression tests prior to each new release to
guarantee stability.

Installation
------------

See INSTALL.md

Quickstart
-----------

To get started, you'll need to connect to the database. If you cloned the
repository from Github, then the database will be in the OpenWormData
subdirectory. You can read it in by doing:

```python
>>> import PyOpenWorm as P
>>> P.connect('PyOpenWorm/default.conf')

```

Then you can try out a few things:

```python

# Grabs the representation of the neuronal network
>>> net = P.Worm().get_neuron_network()

# Grab a specific neuron
>>> aval = net.aneuron('AVAL')

>>> list(aval.type())[0]
'interneuron'

#show how many connections go out of AVAL
>>> aval.connection.count('pre')
86

```

More examples
-------------

Returns information about individual neurons::

```python
>>> aval.name()
'AVAL'

#list all known receptors
>>> sorted(aval.receptors())
['GGR-3', 'GLR-1', ... 'NPR-4', 'UNC-8']

#show how many chemical synapses go in and out of AVAL
>>> aval.Syn_degree()
105

```

Returns the list of all neurons::

```python
#NOTE: This is a VERY slow operation right now
>>> len(set(net.neuron_names()))
302
>>> sorted(net.neuron_names())
['ADAL', 'ADAR', ... 'VD8', 'VD9']

```

Returns a set of all muscles::

```python
>>> muscles = P.Worm().muscles()
>>> len(muscles)
158

```
Because the ultimate aim of OpenWorm is to be a platform for biological research,
the physiological data in PyOpenWorm should be uncontroversial and well supported by
evidence.  Using the Evidence type, it is possible to link data and models
to corresponding articles from peer-reviewed literature:

```python
>>> e = P.Evidence(key="Sulston83", author='Sulston et al.', date='1983')
>>> avdl = P.Neuron(name="AVDL")
>>> avdl.lineageName("AB alaaapalr")
Relationship(s=rdflib.term.URIRef('http://openworm.org/entities/Neuron/AVDL'), p=rdflib.term.URIRef('http://openworm.org/entities/Cell/lineageName'), o=rdflib.term.Literal('AB alaaapalr'))
>>> e.asserts(avdl)
Relationship(s=rdflib.term.URIRef('http://openworm.org/entities/Evidence/Sulston83'), p=rdflib.term.URIRef('http://openworm.org/entities/Evidence/asserts'), o=rdflib.term.URIRef('http://openworm.org/entities/Neuron/AVDL'))
>>> e.asserts(avdl.lineageName("AB alaaapalr"))
Relationship(s=rdflib.term.URIRef('http://openworm.org/entities/Evidence/Sulston83'), p=rdflib.term.URIRef('http://openworm.org/entities/Evidence/asserts'), o=rdflib.term.URIRef('http://openworm.org/entities/Relationship/ad1bb78ba8307e126ff62a44d9999104e'))
>>> e.save()

```

Retrieve evidence:
```python
>>> e0 = P.Evidence(author='Sulston et al.', date='1983')
>>> assertions = e0.asserts()

# is the neuron's presence asserted?
>>> avdl in list(e0.asserts())
True

# is the lineageName of the neuron asserted?
>>> avdl.lineageName("AB alaaapalr") in list(e0.asserts())
True

```

For most types (i.e., subclasses of `P.DataObject`) that do not have required
initialization arguments, you can load all members of that type by making an
object of that type and calling `load()`::
```python
>>> neurons = list(P.Neuron().load())
>>> len(neurons)
302

```

See what neurons express a given neuropeptide::
```python
>>> n = P.Neuron()
>>> n.neuropeptide("INS-26")
Relationship(p=rdflib.term.URIRef('http://openworm.org/entities/Neuron/neuropeptide'), o=rdflib.term.Literal('INS-26'))

>>> sorted(x.name() for x in n.load())
['ASEL', 'ASER', 'ASIL', 'ASIR']

```

Get direct access to the RDFLib graph::
```python
>>> P.config('rdf.graph').query("SELECT ?y WHERE { ?x rdf:type ?y }")
<rdflib.plugins.sparql.processor.SPARQLResult object at ...>

```

Returns the C. elegans connectome represented as a [NetworkX](http://networkx.github.io/documentation/latest/) graph::

```python
>>> net.as_networkx()
<networkx.classes.digraph.DiGraph object at ...>

```

Modeling data
--------------

PyOpenWorm also provides access to store and retrieve data about models.

Retrieve an ion channel's models from the database::

```python
# Get data for a subtype of voltage-gated potassium channels
>> kv1 = P.IonChannel('Kv1')
>> mods = list(kv1.models.get())

```

The same type of operation can be used for the experiment data model.

```python
# Get experiment(s) that back up the data model
>> some_model = mods[0]
>> some_model.references.get()

```

Finally, when you're done accessing the database, be sure to disconnect from it::
```python
>>> P.disconnect()

```

More examples can be found [here](http://pyopenworm.readthedocs.org/en/latest/making_dataObjects.html) and [here](https://github.com/openworm/PyOpenWorm/tree/master/examples).

Documentation
-------------

Further documentation [is available online](http://pyopenworm.readthedocs.org).
