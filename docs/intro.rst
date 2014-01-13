PyOpenWorm
===========

Unified data access library for data about the c. elegans anatomy and model for the OpenWorm project

Basic Usage
------------

::

  import openworm
  
  # Grabs the representation of the neuronal network
  net = PyOpenWorm.network()
  
..  iter = net.motor
  
More examples
-------------

..Returns an iter with all motor neurons::

..  net.sensory
  
..Returns an iter with all sensory neurons::

..  nml = net.neuroml

..Returns a NeuroML2 representation of the entire network::

..  rdf = net.rdf
  
Returns information about individual neurons::

  >>>net.aneuron('AVAL').name()
  AVAL
  >>>net.aneuron('AVAL').aval_neuron.type()
  Interneuron
  >>>net.aneuron('DD5').aval_neuron.type()
  Motor
  >>>net.aneuron('PHAL').aval_neuron.type()
  Sensory
  
..Returns a neuron object by name::

..  nx = network.networkx
