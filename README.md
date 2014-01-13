PyOpenWorm
===========

Unified data access library for data about the c. elegans anatomy and model for the OpenWorm project

Basic Usage
------------

```python
  import openworm
  
  # Grabs the representation of the neuronal network
  net = PyOpenWorm.network()
```
  
More examples
-------------
  
Returns information about individual neurons::

```python
  >>>net.aneuron('AVAL').name()
  AVAL
  >>>net.aneuron('AVAL').aval_neuron.type()
  Interneuron
  >>>net.aneuron('DD5').aval_neuron.type()
  Motor
  >>>net.aneuron('PHAL').aval_neuron.type()
  Sensory
```