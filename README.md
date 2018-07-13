[![Build Status](https://travis-ci.org/openworm/PyOpenWorm.png?branch=dev)](https://travis-ci.org/openworm/PyOpenWorm/builds)
[![Docs](https://readthedocs.org/projects/pow-doc/badge/?version=latest)](https://pow-doc.readthedocs.io/en/latest)
[![Stories in Ready](https://badge.waffle.io/openworm/pyopenworm.png?label=ready&title=Ready)](https://waffle.io/openworm/pyopenworm)  [![Coverage Status](https://coveralls.io/repos/github/openworm/PyOpenWorm/badge.svg?branch=dev)](https://coveralls.io/github/openworm/PyOpenWorm?branch=dev)

PyOpenWorm
===========

A data access layer in Python which integrates disparate structures and
representations for *C. elegans* anatomy and physiology. Enables a simple
Python API for asking various questions about the cells of the *C. elegans* and
enabling data sharing for the purpose of building a [data-to-model
pipeline](http://docs.openworm.org/en/latest/projects) for the
[OpenWorm](http://www.openworm.org) project.

Overview
--------
The data and models required to simulate *C. elegans* are highly heterogeneous.
Consequently, from a software perspective, a variety of underlying
representations are needed to store different aspects of the relevant anatomy
and physiology.  For example, a NetworkX representation of the connectome as a
complex graph enables questions to be asked about nearest neighbors of a given
neuron.  An RDF semantic graph representation is useful for reading and writing
annotations about multiple aspects of a neuron, such as what papers have been
written about it, properties it may have such as ion channels and
neurotransmitter receptors, etc.  A NeuroML representation is useful for
answering questions about model morphology and simulation parameters.  A
Blender representation is a full 3D shape definition that can be used for
calculations in 3D space.

The diversity of underlying representations required for OpenWorm presents a
challenge for data integration and consolidation.  PyOpenWorm solves this
challenge with a unified data access layer whereby different representations
are encapsulated into an abstract view.  This allows the user to work with
objects related to the *biological reality of the worm*, and forget about which
representation is being used under the hood.  The worm itself has a unified
sense of neurons, networks, muscles, ion channels, etc. and so should our code.

Relationship to ChannelWorm
-----------------------------
[ChannelWorm](https://github.com/openworm/ChannelWorm) is the sub-project of
OpenWorm which houses ion channel models.  In the future, we expect ChannelWorm
to be a "consumer" of PyOpenWorm.  A PyOpenWorm database will house physical
models, the digitized plots they are derived from (there is a Plot type in
PyOpenWorm), and provide code to put those models into enumerated formats along
with auxillary files or comments.  However, because these projects were not
developed sequentially, there is currently some overlap in functionality, and
PyOpenWorm itself houses a fairly substantial amount of physiological
information about *C. elegans.* Ultimately, the pure core of PyOpenWorm, which
is meant to be a data framework for storing metadata and provenance (i.e.
parameters and trajectories associated with simulations), will be separated out
into standalone functionality.

Versioning data as code
-----------------------

A library that attempts to reliably expose dynamic data can often be broken
because the underlying data sets that define it change over time.  This is
because data changes can cause queries to return different answers than before,
causing unpredictable behavior.

As such, to create a stable foundational library for others to reuse, the
version of the PyOpenWorm library guarantees the user a specific version of the
data behind that library.  In addition, unit tests are used to ensure basic
sanity checks on data are maintained.  As data are improved, the maintainers of
the library can perform appropriate regression tests prior to each new release
to guarantee stability.

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
>>> P.connect('readme.conf')

```

readme.conf:

```json
{
    "rdf.source" : "ZODB",
    "rdf.store_conf" : ".pow/worm.db"
}
```

Then you can try out a few things:

```python
# Make the context
>>> from PyOpenWorm.context import Context
>>> ctx = Context(ident='http://openworm.org/entities/bio#worm0-data')

# Grabs the representation of the neuronal network
>>> from PyOpenWorm.worm import Worm
>>> net = ctx.stored(Worm)().neuron_network()

# Grab a specific neuron
>>> from PyOpenWorm.neuron import Neuron
>>> aval = ctx.stored(Neuron)(name='AVAL')

>>> aval.type.one()
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
>>> aval.connection.count('either', syntype='send')
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
>>> muscles = ctx.stored(Worm)().muscles()
>>> len(muscles)
158

```
Because the ultimate aim of OpenWorm is to be a platform for biological
research, the physiological data in PyOpenWorm should be uncontroversial and
well supported by evidence.  Using the Evidence type, it is possible to link
data and models to corresponding articles from peer-reviewed literature:

```python
>>> from PyOpenWorm.document import Document
>>> from PyOpenWorm.evidence import Evidence

# Make a context for evidence (i.e., statements about other groups of statements)
>>> evctx = Context(ident='http://example.org/evidence/context')

# Make a context for defining domain knowledge
>>> dctx = Context(ident='http://example.org/data/context')
>>> doc = evctx(Document)(key="Sulston83", author='Sulston et al.', date='1983')
>>> e = evctx(Evidence)(key="Sulston83", reference=doc)
>>> avdl = dctx(Neuron)(name="AVDL")
>>> avdl.lineageName("AB alaaapalr")
PyOpenWorm.statement.Statement(subj=Neuron(ident=rdflib.term.URIRef('http://openworm.org/entities/Neuron/AVDL')), prop=PyOpenWorm.cell.Cell_lineageName(owner=Neuron(ident=rdflib.term.URIRef('http://openworm.org/entities/Neuron/AVDL'))), obj=yarom.propertyValue.PropertyValue(rdflib.term.Literal('AB alaaapalr')), context=PyOpenWorm.context.Context(ident="http://example.org/data/context"))


>>> e.supports(dctx.rdf_object)
PyOpenWorm.statement.Statement(subj=Evidence(ident=rdflib.term.URIRef('http://openworm.org/entities/Evidence/Sulston83')), prop=PyOpenWorm.evidence.Evidence_supports(owner=Evidence(ident=rdflib.term.URIRef('http://openworm.org/entities/Evidence/Sulston83'))), obj=ContextDataObject(ident=rdflib.term.URIRef('http://example.org/data/context')), context=PyOpenWorm.context.Context(ident="http://example.org/evidence/context"))

>>> dctx.save_context()
>>> evctx.save_context()

```

Retrieve evidence:
```python
>>> doc = evctx.stored(Document)(author='Sulston et al.', date='1983')
>>> e0 = evctx.stored(Evidence)(reference=doc)
>>> supported_ctx = e0.supports()

# is the neuron's presence asserted?
>>> dctx.identifier == supported_ctx.identifier
True

```

For most types (i.e., subclasses of `P.DataObject`) that do not have required
initialization arguments, you can load all members of that type by making an
object of that type and calling `load()`::
```python
>>> from PyOpenWorm.network import Network
>>> with ctx.stored(Worm, Neuron, Network) as cctx:
...     w = cctx.Worm()
...     net = cctx.Network()
...     w.neuron_network(net)
PyOpenWorm.statement.Statement(subj=Worm(ident=rdflib.term.URIRef('http://openworm.org/entities/Worm/a8020ed8519038a6bbc98f1792c46c97b')), prop=PyOpenWorm.worm.Worm_neuron_network(owner=Worm(ident=rdflib.term.URIRef('http://openworm.org/entities/Worm/a8020ed8519038a6bbc98f1792c46c97b'))), obj=Network(ident=rdflib.term.URIRef('http://openworm.org/entities/Network/ad33294553d7aae0c3c3f4ab331a295a1')), context=PyOpenWorm.context.QueryContext(ident="http://openworm.org/entities/bio#worm0-data"))

...     neur = cctx.Neuron()
...     neur.count()
302

```

See what neurons express a given neuropeptide::
```python
>>> n = ctx.stored(Neuron)()
>>> n.neuropeptide("INS-26")
PyOpenWorm.statement.Statement(subj=Neuron(ident=rdflib.term.Variable('aNeuron_...')), prop=PyOpenWorm.neuron.Neuron_neuropeptide(owner=Neuron(ident=rdflib.term.Variable('aNeuron_...'))), obj=yarom.propertyValue.PropertyValue(rdflib.term.Literal('INS-26')), context=PyOpenWorm.context.QueryContext(ident="http://openworm.org/entities/bio#worm0-data"))

>>> sorted(x.name() for x in n.load())
['ASEL', 'ASER', 'ASIL', 'ASIR']

```

Get direct access to the RDFLib graph::
```python
>>> P.config('rdf.graph').query("SELECT ?y WHERE { ?x rdf:type ?y }")
<rdflib.plugins.sparql.processor.SPARQLResult object at ...>

```

Modeling data
--------------

As described above, ultimately, ion channel models will be part of the
ChannelWorm repository.  And as the project evolves, other models, such as for
reproduction and development, may be housed in their own repositories.  But for
the time being, the PyOpenWorm repository contains specific models as well.
These models will eventually be transferred to an appropriate and independent
data repository within the OpenWorm suite of tools.



```python
# Get data for a subtype of voltage-gated potassium channels
>> kv1 = ctx(IonChannel)('Kv1')
>> mods = list(kv1.models.get())

```

The same type of operation can be used to obtain the experimental data a given
model was derived from.

```python
# Get experiment(s) that back up the data model
>> some_model = mods[0]
>> some_model.references.get()

```

Finally, when you're done accessing the database, be sure to disconnect from it::
```python
>>> P.disconnect()

```

More examples can be found
[here](http://pow-doc.readthedocs.org/en/latest/making_dataObjects.html) and
[here](https://github.com/openworm/PyOpenWorm/tree/master/examples).

Documentation
-------------

Further documentation [is available online](http://pow-doc.readthedocs.org).

Questions?
----------
[Join the Slack chat](https://openworm.slack.com/messages/C02EPNMP1/) for
clarification, to ask questions, or just to say, 'Hi'.
