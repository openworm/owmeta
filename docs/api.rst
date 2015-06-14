.. _api:

Draft Updates and Modifications to the PyOpenWorm API
======================================================

This API will augment the existing API of `PyOpenWorm <https://github.com/openworm/PyOpenWorm/>`_, which is centered around a simple means of accessing data about the C. elegans using an object model that is based on its anatomy.  In particular it is for making statements about biological entities in the worm or querying previously made statements. In addition, statements concerning the evidence for statements (called relationships below).

Many of these new API calls are designed around the principle that most statements correspond to some action on the database. Some of these actions may be complex, but intuitively ``a.B()``, the Query form, will query against the database for the value or values that are related to ``a`` through ``B``; on the other hand, ``a.B(c)``, the Update form, will add a statement to the database that ``a`` relates to ``c`` through ``B``. For the Update form, a Relationship object describing the relationship stated is returned as a side-effect of the update.

Relationship objects are key to the `Evidence class <#evidence>`_ for making statements which can be sourced. Relationships can themselves be members in a relationship, allowing for fairly complex statements to be made about entities.

Notes

- Of course, when these methods communicate with an external database, they may fail due to the database being unavailable and the user should be notified if a connection cannot be established in a reasonable time. Also, some objects are created by querying the database; these may be made out-of-date in that case.
- Some terms may be unexplained
- ``a : {x_0,...,x_n}`` means ``a`` could have the value of any one of ``x_0`` through ``x_n``




Morphology = neuroml.Morphology
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Physical cell structure


Muscle(name : String)
~~~~~~~~~~~~~~~~~~~~~~
A representation of a muscle cell. `See also: current API`

Muscle.receptor() : ListOf(Receptor)
++++++++++++++++++++++++++++++++++++++

Get a list of receptors for this muscle

Muscle.receptor(receptor : Receptor) : Relationship
++++++++++++++++++++++++++++++++++++++++++++++++++++

State that this muscle has the given receptor type

Muscle.innervatedBy() : ListOf(Neuron)
++++++++++++++++++++++++++++++++++++++++

Get a list of neurons that synapse on this muscle cell

Muscle.innervatedBy(n : Neuron) : Relationship
+++++++++++++++++++++++++++++++++++++++++++++++

State that the muscle is innervated by n and return the Relationship object that captures that.

Receptor = String
~~~~~~~~~~~~~~~~~

Network()
~~~~~~~~~~

A network of Neurons. `see current API`

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
