PyOpenWorm
===========

Unified data access library for data about the c. elegans anatomy and model for the OpenWorm project

Basic Usage
------------

::

  import openworm
  
  # Grabs the representation of the neuronal network
  net = PyOpenWorm.network()
  
More examples
-------------
  
Returns information about individual neurons::

  >>>net.aneuron('AVAL').name()
  AVAL
  >>>net.aneuron('AVAL').type()
  Interneuron
  >>>net.aneuron('DD5').type()
  Motor
  >>>net.aneuron('PHAL').type()
  Sensory
  #show how many gap junctions go in and out of AVAL
  >>>net.aneuron('AVAL').GJ_degree()
  60
  #show how many chemical synapses go in and out of AVAL
  >>>net.aneuron('AVAL').Syn_degree()
  74
  
  
