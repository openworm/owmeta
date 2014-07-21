[![Build Status](https://travis-ci.org/openworm/PyOpenWorm.png?branch=alpha0.5)](https://travis-ci.org/openworm/PyOpenWorm)

PyOpenWorm
===========

Unified data access library for data about the c. elegans anatomy and model for the OpenWorm project

What does it do?
----------------

Allows asking various questions about the c. elegans nervous system.

Basic Usage
-----------

```python
  >>>import PyOpenWorm
  
  # Grabs the representation of the neuronal network
  >>>net = PyOpenWorm.Worm().get_neuron_network()
  >>>list(net.aneuron('AVAL').type())
  ['Interneuron']
  #show how many gap junctions go in and out of AVAL
  >>>net.aneuron('AVAL').connection.count('either',syntype='gapjunction')
  80
```
  
  
More examples
-------------
  
Returns information about individual neurons::

```python
  >>>list(net.aneuron('AVAL').name())
  ['AVAL']
  #list all known receptors
  >>>list(net.aneuron('AVAL').receptors())
  ['GLR-1', 'NMR-1', 'GLR-4', 'GLR-2', 'GGR-3', 'UNC-8', 'GLR-5', 'NMR-2']
  >>>list(net.aneuron('DD5').type())
  ['motor']
  >>>net.aneuron('PHAL').type()
  ['sensory']
  #show how many chemical synapses go in and out of AVAL
  >>>net.aneuron('AVAL').Syn_degree()
  74
```

Returns the list of all neurons::

```python
  >>>  len(set(net.neurons()))
  302
```

Returns the list of all muscles::

```python
  >>>'MDL08' in PyOpenWorm.Worm().muscles()
  True
```


Returns provenance information providing evidence about facts::

```python
  >>>ader = PyOpenWorm.Neuron('ADER')
  >>>list(ader.receptors())
  ['ACR-16', 'TYRA-3', 'DOP-2', 'EXP-1']
  #look up what reference says this neuron has a receptor EXP-1
  >>>e = Evidence()
  >>>e.asserts(PyOpenWorm.Neuron('ADER').receptor('EXP-1')) 
  >>>list(e.doi())
  ['10.100.123/natneuro']
```

Returns the c. elegans connectome represented as a [NetworkX](http://networkx.github.io/documentation/latest/) graph::

```python
  >>>net.as_networkx()
  <networkx.classes.digraph.DiGraph object at 0x10f28bc10>
```

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

Installation
------------

    git clone https://github.com/openworm/PyOpenWorm.git
    cd PyOpenWorm
    python setup.py install
    
Uninstall
----------

    pip uninstall PyOpenWorm

Running tests
-------------

After checking out the project, tests can be run on the command line with::

    python -m unittest discover -s tests
