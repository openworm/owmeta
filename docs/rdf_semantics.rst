.. _rdf_semantics:

RDF semantics for |pow|
=======================

*It may be helpful to read this document together with* :ref:`the RDF structure document <rdf_format>`.

In the context of |pow|, biological objects are classes of, for instance, anatomical features of a worm. That is to say, statements made about C. elegans are not about a specific worm, but are stated about the entire class of worms. The semantics of a ``property SimpleProperty/value value`` triple are that if any value is set, then without any additional statements being made, an instance of the object has been observed to have the value at some point in time, somewhere, under some set of conditions. In other words, the statement is an existential quantification over the associated object(class).

The purpose of the identifiers for Properties is to allow statements to be made about them directly. An example::

    <http://openworm.org/entities/Entity/1> <http://openworm.org/entities/Entity/interactsWith> <http://openworm.org/entities/Entity_interactsWith/2> .
    <http://openworm.org/entities/Entity_interactsWith/2> <http://openworm.org/entities/SimpleProperty/value> <http://openworm.org/entities/Entity/3> .

    <http://openworm.org/entities/Entity/4> <http://openworm.org/entities/Entity/modulates> <http://openworm.org/entities/Entity_modulates/5> .
    <http://openworm.org/entities/Entity_modulates/5> <http://openworm.org/entities/SimpleProperty/value> <http://openworm.org/entities/Entity_interactsWith/2>
