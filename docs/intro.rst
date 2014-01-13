libopenworm
===========

Unified data access library for data about the c. elegans anatomy and model for the OpenWorm project

Basic Usage
------------

```python
  import openworm
  
  # Grabs the representation of the neuronal network
  network = openworm.network
  
  iter = network.motor
```
  
More examples
-------------

### Returns an iter with all motor neurons

```python
  network.sensory
```  
  
### Returns an iter with all sensory neurons

```python
  nml = network.neuroml
```

### Returns a NeuroML2 representation of the entire network

```python
  rdf = network.rdf
```  
  
### Returns an RDF graph representation of the entire network

```python
  aval_neuron = network['AVAL']
```
  
### Returns a neuron object by name

```python
  nx = network.networkx
```