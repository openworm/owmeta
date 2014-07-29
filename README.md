[![Build Status](https://travis-ci.org/openworm/PyOpenWorm.png?branch=alpha0.5)](https://travis-ci.org/openworm/PyOpenWorm)

PyOpenWorm
===========

Unified data access library for data about the C. elegans anatomy and model for the OpenWorm project

What does it do?
----------------

Allows asking various questions about the C. elegans nervous system.

Basic Usage
-----------

To get started::

```python
  >>> import PyOpenWorm

  # Set up
  >>> PyOpenWorm.connect('default.conf')
  # Grabs the representation of the neuronal network
  >>> net = PyOpenWorm.Worm().get_neuron_network()
  >>> list(net.aneuron('AVAL').type())
  #show how many gap junctions go in and out of AVAL
  >>> net.aneuron('AVAL').connection.count('either',syntype='gapjunction')
  80
  # Tear down
  >>> PyOpenWorm.disconnect()
```

default.conf::

```python
    {
        "connectomecsv" : "https://raw.github.com/openworm/data-viz/master/HivePlots/connectome.csv",
        "neuronscsv" : "https://raw.github.com/openworm/data-viz/master/HivePlots/neurons.csv",
        "sqldb" : "/home/markw/work/openworm/PyOpenWorm/db/celegans.db",
        "rdf.source" : "default",
        "rdf.store" : "Sleepycat",
        "rdf.store_conf" : "worm.db",
        "user.email" : "jerry@cn.com",
        "rdf.upload_block_statement_count" : 50,
        "test_variable" : "test_value"
    }
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

Add provenance information::

```python
  >>> e = Evidence(author='Sulston et al.', date='1983')
  >>> e.asserts(Neuron(name="AVDL").lineageName("AB alaaapalr"))
  <PyOpenWorm.dataObject.Evidence_asserts at 0x27f3d50>
  >>> e.save()
```

See what some evidence stated::
```python
  >>> e0 = Evidence(author='Sulston et al.', date='1983')
  >>> list(e0.asserts())
  [Neuron(name=AVDL,lineageName=AB alaaapalr)]
```

See what neurons express some receptor::
```python
  >>>n = Neuron()
  >>>n.receptor("TH")
  >>>list(n.load())
  [Neuron(lineageName=, name=CEPVL, Neighbor(), Connection(), type=, receptor=, innexin=),
   Neuron(lineageName=, name=CEPVR, Neighbor(), Connection(), type=, receptor=, innexin=),
   Neuron(lineageName=, name=PDEL, Neighbor(), Connection(), type=, receptor=, innexin=),
   Neuron(lineageName=, name=PDER, Neighbor(), Connection(), type=, receptor=, innexin=),
   Neuron(lineageName=, name=CEPDL, Neighbor(), Connection(), type=, receptor=, innexin=),
   Neuron(lineageName=, name=CEPDR, Neighbor(), Connection(), type=, receptor=, innexin=)]
```

To get any object's possible values, use load()::
```python
  >>>list(P.Neuron().load())
  [
   ...
   Neuron(lineageName=, name=IL1DL, Neighbor(), Connection(), type=, receptor=, innexin=),
   Neuron(lineageName=, name=OLQDL, Neighbor(), Connection(), type=, receptor=VGluT, innexin=),
   Neuron(lineageName=, name=OLQDL, Neighbor(), Connection(), type=, receptor=EAT-4, innexin=),
   Neuron(lineageName=, name=OLQDL, Neighbor(), Connection(), type=, receptor=, innexin=),
   Neuron(lineageName=, name=IL1DR, Neighbor(), Connection(), type=, receptor=, innexin=),
   Neuron(lineageName=, name=IL1R, Neighbor(), Connection(), type=, receptor=, innexin=),
   Neuron(lineageName=, name=AVER, Neighbor(), Connection(), type=, receptor=FLP-1, innexin=),
   Neuron(lineageName=, name=AVER, Neighbor(), Connection(), type=, receptor=, innexin=),
   ...
  ]
  # Properties are a little different
  >>>next(Neuron().receptor.load())
  receptor=INS-1;FLP-6;FLP-21;FLP-20;NLP-21...

```

Get direct access to the RDFLib graph::
```python
 # we get it from Worm, but any object will do
 >>> Worm().rdf.query(...)
 ```

Use pre-made objects with custom SPARQL queries::
```python
 >>> n = Neuron()
 # Get a Neuron graph pattern suitable for use in a SPARQL query
 >>> gp = n.graph_pattern(query=True)
 >>> print gp
 <http://openworm.org/entities/Neuron/cc3414e079869baf6c9ef3105545632fb8c1e3eddc2f3300311dc160> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://openworm.org/entities/Neuron> .
 <http://openworm.org/entities/Neuron/cc3414e079869baf6c9ef3105545632fb8c1e3eddc2f3300311dc160> <http://openworm.org/entities/Neuron/lineageName> ?Neuron_lineageName6836ce3c9c85873e .
 ?Neuron_lineageName6836ce3c9c85873e <http://openworm.org/entities/SimpleProperty/value> ?lineageName .
 <http://openworm.org/entities/Neuron_name/8268f38298d4ce45fdaac56cada0724575774a472a6055ac40233665> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://openworm.org/entities/Neuron_name> .
 <http://openworm.org/entities/Neuron/cc3414e079869baf6c9ef3105545632fb8c1e3eddc2f3300311dc160> <http://openworm.org/entities/Neuron/name> <http://openworm.org/entities/Neuron_name/8268f38298d4ce45fdaac56cada0724575774a472a6055ac40233665> .
 <http://openworm.org/entities/Neuron_name/8268f38298d4ce45fdaac56cada0724575774a472a6055ac40233665> <http://openworm.org/entities/SimpleProperty/value> "PVCR" .
 <http://openworm.org/entities/Neuron/cc3414e079869baf6c9ef3105545632fb8c1e3eddc2f3300311dc160> <http://openworm.org/entities/Neuron/type> ?Neuron_type7b9bf83eb590323f .
 ?Neuron_type7b9bf83eb590323f <http://openworm.org/entities/SimpleProperty/value> ?type .
 <http://openworm.org/entities/Neuron/cc3414e079869baf6c9ef3105545632fb8c1e3eddc2f3300311dc160> <http://openworm.org/entities/Neuron/receptor> ?Neuron_receptor986e983db972bd3e .
 ?Neuron_receptor986e983db972bd3e <http://openworm.org/entities/SimpleProperty/value> ?receptor .
 <http://openworm.org/entities/Neuron/cc3414e079869baf6c9ef3105545632fb8c1e3eddc2f3300311dc160> <http://openworm.org/entities/Neuron/innexin> ?Neuron_innexind9223b3f5feebd3d .
 ?Neuron_innexind9223b3f5feebd3d <http://openworm.org/entities/SimpleProperty/value> ?innexin

 # Run a query to get bare values
 >>> for x in n.rdf.query("SELECT DISTINCT ?name ?innexin WHERE { "+ n.graph_pattern(True) +" filter(?innexin != <http://openworm.org/entities/variable#innexin>) }"):
 ...    print x
 (rdflib.term.Literal(u'AIYR'), rdflib.term.Literal(u'INX-1'))
 (rdflib.term.Literal(u'AIYR'), rdflib.term.Literal(u'INX-7'))
 (rdflib.term.Literal(u'AIYR'), rdflib.term.Literal(u'INX-19'))
 (rdflib.term.Literal(u'AIYR'), rdflib.term.Literal(u'UNC-9'))
 # ...
 ```

Returns the c. elegans connectome represented as a [NetworkX](http://networkx.github.io/documentation/latest/) graph::

```python
  >>>net.as_networkx()
  <networkx.classes.digraph.DiGraph object at 0x10f28bc10>
```

More examples can be found [here](http://pyopenworm-markw.readthedocs.org/en/latest/making_dataObjects.html) and [here](https://github.com/openworm/PyOpenWorm/tree/alpha0.5/examples).

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
