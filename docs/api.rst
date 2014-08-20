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

Worm()
~~~~~~~~

A representation of the whole worm

Worm.neuron_network() : Network
+++++++++++++++++++++++++++++++++

Return the neuron Network of the worm

Worm.cells() : Population
+++++++++++++++++++++++++++

Return the Population of all cells in the worm

.. _evidence:

Evidence(key = value)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A representation of some document which provides evidence for something. Possible keys include::
    
    pmid,pubmed: a pubmed id or url (e.g., 24098140)
    wbid,wormbase: a wormbase id or url (e.g., WBPaper00044287)
    doi: a Digitial Object id or url (e.g., s00454-010-9273-0)

Evidence.asserts(relationship : Relationship) : Relationship
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

State that this Evidence asserts that the relationship is true.

Example::

    import bibtex
    bt = bibtex.parse("my.bib")
    n1 = Neuron("AVAL")
    n2 = Neuron("DA3")
    c = Connection(pre=n1,post=n2,class="synapse")
    e = Evidence(bibtex=bt['white86'])
    e.asserts(c)

Other methods return objects which asserts accepts.

Example::

    n1 = Neuron("AVAL")
    r = n1.neighbor("DA3")
    e = Evidence(bibtex=bt['white86'])
    e.asserts(r)

Evidence.asserts() : ListOf(Relationship)
+++++++++++++++++++++++++++++++++++++++++++

Returns a sequence of statements asserted by this evidence

Example::

    import bibtex
    bt = bibtex.parse("my.bib")
    n1 = Neuron("AVAL")
    n2 = Neuron("DA3")
    c = Connection(pre=n1,post=n2,class="synapse")
    e = Evidence(bibtex=bt['white86'])
    e.asserts(c)
    list(e.asserts()) # Returns a list [..., d, ...] such that d==c

Evidence.author() : ListOf(String)
++++++++++++++++++++++++++++++++++

Returns a list of author names

Relationship
~~~~~~~~~~~~~

Abstract class. A relationship between two entities. 

Relationship.pull(class : python class, method_name : String) : SetOf(Relationship)
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Returns a set of Relationship objects associated with the call ``class.method_name()``

Cell(name : String)
~~~~~~~~~~~~~~~~~~~

A biological cell

Cell.lineageName() : ListOf(String)
+++++++++++++++++++++++++++++++++++++++++++

Return the lineage name. Multiplicity may result from developmental differences

Example::

    c = Cell(name="ADAL")
    c.lineageName() # Returns ["AB plapaaaapp"]

Cell.blast() : String
++++++++++++++++++++++++++++

Return the blast name.

Example::

    c = Cell(name="ADAL")
    c.blast() # Returns "AB"


Cell.parentOf() : ListOf(Cell)
++++++++++++++++++++++++++++++++

Return the direct daughters of the cell in terms of developmental lineage.

Example::

    c = Cell(lineageName="AB plapaaaap")
    c.parentOf() # Returns [Cell(lineageName="AB plapaaaapp"),Cell(lineageName="AB plapaaaapa")]

Cell.daughterOf() : ListOf(Cell)
++++++++++++++++++++++++++++++++++

Return the parent(s) of the cell in terms of developmental lineage.  

Example::

    c = Cell(lineageName="AB plapaaaap")
    c.daughterOf() # Returns [Cell(lineageName="AB plapaaaa")]


Cell.divisionVolume() : Quantity
++++++++++++++++++++++++++++++++++++++

Return the volume of the cell at division during development

Example::

    c = Cell(lineageName="AB plapaaaap")

Cell.divisionVolume(volume : Quantity) : Relationship
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Set the volume of the cell at division

Example::

    v = Quantity("600","(um)^3")
    c = Cell(lineageName="AB plapaaaap")
    c.divisionVolume(v)

Cell.morphology() : Morphology
+++++++++++++++++++++++++++++++++++

Return the morphology of the cell. Currently this is restricted to `Neuron <#neuron>`_ objects.

Morphology = neuroml.Morphology
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Physical cell structure

Neuron(name : String)
~~~~~~~~~~~~~~~~~~~~~

A subclass of Cell

Neuron.connection() : ListOf(Connection)
+++++++++++++++++++++++++++++++++++++++++++

Get a set of Connection objects describing chemical synapses or gap junctions between this neuron and others

Neuron.neighbor() : ListOf(Neuron)
+++++++++++++++++++++++++++++++++++

Get the neighboring Neurons

Neuron.neighbor(neuronName : String) : Connection
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

State that neuronName is a neighbor of this Neuron

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

Connection(pre : Neuron, post : Neuron, [strength : Integer, ntrans : Neurotransmitter, type : ConnectionType ] )
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A representation of the connection between neurons. Either a gap junction or a chemical synapse

Connection.type() : ConnectionType
+++++++++++++++++++++++++++++++++++++++++++++++++++++

Returns the type of connection: 'gap junction' or 'synapse' as a String

Connection.type(type : ConnectionType) : Relationship
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

State that the connection is a gap junction/chemical synapse

Connection.neurotransmitter() : String
+++++++++++++++++++++++++++++++++++++++++++++++++
Returns the type of neurotransmitter used in the connection as a String

Connection.strength() : Integer
++++++++++++++++++++++++++++++++
Returns the connection strength, the number of synapses and / or gap junctions made between the neurons

ConnectionType = {'gap junction', 'synapse'}
+++++++++++++++++++++++++++++++++++++++++++++

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
