.. _futureapi:

The following API calls do not yet exist, but would be excellent next functions
to implement

Population()
~~~~~~~~~~~~~~~~~~~~~~~~~~~
A collection of cells. Constructor creates an empty population.

Population.filterCells(filters : ListOf(PairOf(unboundMethod, methodArgument))) : Population
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Allows for groups of cells to be created based on shared properties including neurotransmitter, anatomical location or region, cell type.

Example::

    p = Worm.cells()
    p1 = p.filterCells([(Cell.lineageName, "AB")]) # A population of cells with AB as the blast cell

NeuroML()
~~~~~~~~~~

A utility for generating NeuroML files from other objects. The semantics described `above <#draft-api>`__ do not apply here.

NeuroML.generate(object : {Network, Neuron, IonChannel}, type : {0,1,2}) : neuroml.NeuroMLDocument
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Get a NeuroML object that represents the given object. The ``type`` determines what content is included in the NeuroML object:

- 0=full morphology+biophysics
- 1=cell body only+biophysics
- 2=full morphology only

NeuroML.write(document : neuroml.NeuroMLDocument, filename : String)
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Write out a NeuroMLDocument
