[![Build Status](https://travis-ci.org/openworm/PyOpenWorm.png?branch=alpha0.5)](https://travis-ci.org/openworm/PyOpenWorm)

PyOpenWorm
===========

A unified, simple data access library for data & facts about *C. elegans* biology

What does it do?
----------------

Enables a simple API for asking various questions about the cells of the *C. elegans*, enabling the sharing of data about *C. elegans* for the purpose of building a data-to-model pipeline for the OpenWorm project.

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

Basic Usage
-----------

You may need to install some dependencies in order to use PyOpenWorm. These can be installed with:

    python setup.py develop --user

To get started, you'll probably want to load in the database. If you cloned the repository from Github, then the database will be in the OpenWormData subdirectory. You can read it in
by doing 

```python
  >>> import PyOpenWorm as P
  >>> P.connect('PyOpenWorm/default.conf')

  >>> P.loadData('OpenWormData/out.n3', 'n3')

  >>> P.disconnect()

```

Then you can try out a few things:

```python
  # Set up
  >>> P.connect('PyOpenWorm/default.conf')

  # Grabs the representation of the neuronal network
  >>> net = P.Worm().get_neuron_network()
  >>> list(net.aneuron('AVAL').type())
  ['interneuron']

  #show how many connections go out of AVAL
  >>> net.aneuron('AVAL').connection.count('pre')
  77

```
  
  
More examples
-------------
  
Returns information about individual neurons::

```python
  >>> list(net.aneuron('AVAL').name())
  ['AVAL']

  #list all known receptors
  >>> s = set(net.aneuron('AVAL').receptors())
  >>> s == set(['GLR-1', 'NMR-1', 'GLR-4', 'GLR-2', 'GGR-3', 'UNC-8', 'GLR-5', 'NMR-2'])
  True

  >>> list(net.aneuron('DD5').type())
  ['motor']
  >>> list(net.aneuron('PHAL').type())
  ['sensory']

  #show how many chemical synapses go in and out of AVAL
  >>> net.aneuron('AVAL').Syn_degree()
  74

```

Returns the list of all neurons::

```python
  >>> len(set(P.Neuron().load()))
  302

```

Returns the list of all muscles::

```python
  >>> 'MDL08' in (x.name.one() for x in P.Worm().muscles())
  True

```


Returns provenance information providing evidence about facts::

```python
  >>> ader = P.Neuron('ADER')
  >>> s = set(ader.receptors())
  >>> s == set(['ACR-16', 'TYRA-3', 'DOP-2', 'EXP-1'])
  True

  #look up what reference says this neuron has a receptor EXP-1
  >>> e = P.Evidence()
  >>> e.asserts(P.Neuron('ADER').receptor('EXP-1')) 
  asserts=receptor=EXP-1
  >>> list(e.doi())
  ['10.100.123/natneuro']

```

Add provenance information::

```python
  >>> e = P.Evidence(author='Sulston et al.', date='1983')
  >>> e.asserts(P.Neuron(name="AVDL").lineageName("AB alaaapalr"))
  asserts=lineageName=AB alaaapalr
  >>> e.save()

```

See what some evidence stated::
```python
  >>> e0 = P.Evidence(author='Sulston et al.', date='1983')
  >>> list(e0.asserts())
  [Neuron(name=AVDL,lineageName=AB alaaapalr)]

```

See what neurons express some receptor::
```python
  >>> n = P.Neuron()
  >>> n.receptor("TH")
  receptor=TH

  >>> s = set(x.name.one() for x in n.load()) 
  >>> s == set(['CEPVL','CEPVR','PDEL','PDER','CEPDR'])
  True

```

To get any object's possible values, use load()::
```python
  >>> list(P.Neuron().load())
  >>>
    set(['IL1DL',
    'OLQDL',
    'OLQDL',
    'OLQDL',
    'IL1DR',
    'IL1R', 
    'AVER', 
    'AVER'])
  [
   ...
   Neuron(lineageName=, name= Neighbor(), Connection(), type=, receptor=, innexin=),
   Neuron(lineageName=, name= Neighbor(), Connection(), type=, receptor=VGluT, innexin=),
   Neuron(lineageName=, name= Neighbor(), Connection(), type=, receptor=EAT-4, innexin=),
   Neuron(lineageName=, name= Neighbor(), Connection(), type=, receptor=, innexin=),
   Neuron(lineageName=, name= Neighbor(), Connection(), type=, receptor=, innexin=),
   Neuron(lineageName=, name=Neighbor(), Connection(), type=, receptor=, innexin=),
   Neuron(lineageName=, name=Neighbor(), Connection(), type=, receptor=FLP-1, innexin=),
   Neuron(lineageName=, name=Neighbor(), Connection(), type=, receptor=, innexin=),
   ...
  ]
  # Properties are a little different
  >>> next(P.Neuron().receptor.load())
  receptor=INS-1;FLP-6;FLP-21;FLP-20;NLP-21...

```

Get direct access to the RDFLib graph::
```python
 # we get it from Worm, but any object will do
 >>> Worm().rdf.query(...)

```

Returns the c. elegans connectome represented as a [NetworkX](http://networkx.github.io/documentation/latest/) graph::

```python
  >>> net.as_networkx()
  <networkx.classes.digraph.DiGraph object at 0x10f28bc10>

```

More examples can be found [here](http://pyopenworm.readthedocs.org/en/alpha0.5/making_dataObjects.html) and [here](https://github.com/openworm/PyOpenWorm/tree/alpha0.5/examples).


Ease of use
-----------

This library should be easy to use and easy to install, to make it most accessible.  Python beginners should be able to get information out about c. elegans from this library.  Sytactical constructs in this library should be intuitive and easy to understand what they will return within the knowledge domain of c. elegans, 
rather than in the programming domain of its underlying technologies.  Values that are returned should be easily interpretable and easy to read.
Wherever possible, pure-python libraries or those with few compilation requirements, rather than those that create extra dependencies on external native libraries are used.

Installation
------------

See INSTALL.md
