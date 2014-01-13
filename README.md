PyOpenWorm
===========

Unified data access library for data about the c. elegans anatomy and model for the OpenWorm project

What does it do?
----------------

Allows asking various questions about the c. elegans nervous system.

Basic Usage
-----------

```python
  >>>import openworm
  
  # Grabs the representation of the neuronal network
  >>>net = PyOpenWorm.Network()
  >>>net.aneuron('AVAL').type()
  Interneuron
  #show how many gap junctions go in and out of AVAL
  >>>net.aneuron('AVAL').GJ_degree()
  60
```
  
  
More examples
-------------
  
Returns information about individual neurons::

```python
  >>>net.aneuron('AVAL').name()
  AVAL
  >>>net.aneuron('DD5').type()
  Motor
  >>>net.aneuron('PHAL').type()
  Sensory
  #show how many chemical synapses go in and out of AVAL
  >>>net.aneuron('AVAL').Syn_degree()
  74
```

Returns the c. elegans connectome represented as a [NetworkX](http://networkx.github.io/documentation/latest/) graph::

```python
  >>>net.as_networkx()
  <networkx.classes.digraph.DiGraph object at 0x10f28bc10>
```