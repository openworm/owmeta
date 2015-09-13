[![Build Status](https://travis-ci.org/openworm/PyOpenWorm.png?branch=dev)](https://travis-ci.org/openworm/PyOpenWorm/builds)
[![Docs](https://readthedocs.org/projects/pyopenworm/badge/?version=latest)](https://pyopenworm.readthedocs.org/en/latest)
[![Join the chat at https://gitter.im/openworm/pyopenworm](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/openworm/pyopenworm?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge) [![Stories in Ready](https://badge.waffle.io/openworm/pyopenworm.png?label=ready&title=Ready)](https://waffle.io/openworm/pyopenworm)  [![Coverage Status](https://coveralls.io/repos/openworm/PyOpenWorm/badge.svg?branch=dev&service=github)](https://coveralls.io/github/openworm/PyOpenWorm?branch=dev)  [![Code Climate](https://codeclimate.com/github/openworm/PyOpenWorm/badges/gpa.svg)](https://codeclimate.com/github/openworm/PyOpenWorm)

PyOpenWorm
===========

A unified, simple data access library in Python for data, facts, and models of
*C. elegans* anatomy for the [OpenWorm project](http://www.openworm.org)

What does it do?
----------------

Enables a simple Python API for asking various questions about the cells of the
*C. elegans*, enabling the sharing of data about *C. elegans* for the purpose
of building a [data-to-model pipeline](http://docs.openworm.org/en/latest/projects)
for the OpenWorm project.  In addition, it is a repository for various iterations
of inferred / predicted data about *C. elegans*.  Uncontroversial facts and
inferred information are distinguished through the use of explicit Evidence
references.

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
>>> P.connect()

```

Then you can try out a few things:

```python

# Grabs the representation of the neuronal network
>>> net = P.Worm().get_neuron_network()

# Grab a specific neuron
>>> aval = net.aneuron('AVAL')

>>> aval.type()
set([u'interneuron'])

#show how many connections go out of AVAL
>>> aval.connection.count('pre')
77

```

How to use this library
-----------------------

PyOpenWorm enables making statements about biological entities in the worm or
querying previously made statements. In addition, statements may concern the
evidence for statements, called Relationships.  ``a.B()``, the Query form, will
query against the database for the value or values that are related to ``a``
through ``B``; on the other hand, ``a.B(c)``, the Update form, will add a
statement to the database that ``a`` relates to ``c`` through ``B``. For the
Update form, a Relationship object describing the relationship stated is
returned as a side-effect of the update.

Relationship objects are key to the `Evidence class <#evidence>`_ for making
statements which can be sourced. Relationships can themselves be members in a
relationship, allowing for fairly complex statements to be made about entities.

Why is this necessary?
----------------------

There are many different useful ways to compute with data related to the worm.
Different data structures have different strengths and answer different questions.
For example, a NetworkX representation of the connectome as a complex graph enables
questions to be asked about first and second nearest neighbors of a given neuron.
In contrast, an RDF semantic graph representation is useful for reading and
writing annotations about multiple aspects of a neuron, such as what papers
have been written about it, multiple different properties it may have such as
ion channels and neurotransmitter receptors.  A NeuroML representation is useful
for answering questions about model morphology and simulation parameters.  Lastly,
a Blender representation is a full 3D shape definition that can be used for
calculations in 3D space.  Further representations regarding activity patterns
such as Neo or simulated activity can be considered as well.

Using these different representations separately leads to ad hoc scripting for
for each representation.  This presents a challenge for data integration and
consolidation of information in 'master' authoritative representations.  By
creating a unified data access layer, different representations
can become encapsulated into an abstract view.  This allows the user to work with
objects related to the biological reality of the worm.  This has the advantage that
the user can forget about which representation is being used under the hood.  

The worm itself has a unified sense of neurons, networks, muscles,
ion channels, etc and so should our code.

More examples
-------------

Returns information about individual neurons::

```python
>>> aval.name()
u'AVAL'

#list all known receptors
>>> sorted(aval.receptors())
[u'GGR-3', u'GLR-1', u'GLR-2', u'GLR-4', u'GLR-5', u'NMR-1', u'NMR-2', u'UNC-8']

#show how many chemical synapses go in and out of AVAL
>>> aval.Syn_degree()
90

```

Returns the list of all neurons::

```python
#NOTE: This is a VERY slow operation right now
>>> len(set(net.neuron_names()))
302
>>> sorted(list(net.neuron_names())) # doctest:+ELLIPSIS
[u'ADAL', u'ADAR', ... u'VD8', u'VD9']

```

Returns a set of all muscles::

```python
>>> muscles = P.Worm().muscles()
>>> len(muscles)
96

```

Add some evidence::

```python
>>> e = P.Evidence(key="Sulston83", author='Sulston et al.', date='1983')
>>> avdl = P.Neuron(name="AVDL")
>>> avdl.lineageName("AB alaaapalr")
lineageName=`AB alaaapalr'
>>> e.asserts(avdl)
asserts=`AVDL'
>>> e.asserts(avdl.lineageName) # doctest:+ELLIPSIS
asserts=...
>>> e.save()

```

See what some evidence stated::
```python
>>> e0 = P.Evidence(author='Sulston et al.', date='1983')
>>> assertions = e0.asserts()

# is the neuron's presence asserted?
>>> avdl in list(e0.asserts())
True

# is the lineageName of the neuron asserted?
>>> avdl.lineageName in list(e0.asserts())
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

See what neurons express some neuropeptide::
```python
>>> n = P.Neuron()
>>> n.neuropeptide("INS-26")
neuropeptide=`INS-26'

>>> s = set(x.name() for x in n.load())
>>> s == set(['ASEL', 'ASER', 'ASIL', 'ASIR'])
True

```

See what neurons innervate a muscle::
```python
>>> mdr21 = P.Muscle('MDR21')
>>> innervates_mdr21 = mdr21.innervatedBy()
>>> len(innervates_mdr21)
4

```

Get direct access to the RDFLib graph::
```python
>>> P.config('rdf.graph').query("SELECT ?y WHERE { ?x rdf:type ?y }") # doctest:+ELLIPSIS
<rdflib.plugins.sparql.processor.SPARQLResult object at ...>

```

Returns the C. elegans connectome represented as a [NetworkX](http://networkx.github.io/documentation/latest/) graph::

```python
>>> net.as_networkx() # doctest:+ELLIPSIS
<networkx.classes.digraph.DiGraph object at ...>

```

Modelling data
--------------

PyOpenWorm also provides access to store and retrieve data about models.
Following are some examples of these types of operations.

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

Ease of use
-----------

PyOpenWorm should be easy to use and easy to install, to make it most accessible.  
Python beginners should be able to get information out about c. elegans from
this library.  

Syntactical constructs in this library should be intuitive and easy
to understand what they will return within the knowledge domain of c. elegans,
rather than in the programming domain of its underlying technologies.  Values that
are returned should be easily interpretable and easy to read.

Wherever possible, pure-python libraries or those with few compilation requirements,
rather than those that create extra dependencies on external native libraries are used.

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

Making it easy to get out authoritative data, keeping inferred data as an advanced feature
------------------------------------------------------------------------------------------

In an effort to make the library most helpful to experimental scientists, PyOpenWorm
strives to keep the easiest-to-access features of this API only returning data that is
uncontroversial and well supported by evidence.  At the same time, there is an
important need to incorporate information that may not be confirmed by observation,
and instead is the result of an inference process.  These inferred data will also
be marked with evidence that clearly indicates its status as not authoritative.
PyOpenWorm endeavors to make the access to inferred data clearly separate from
uncontroversial data reported in peer-reviewed literature.
