.. _rdf_details:

RDF semantics for |owm|
=======================

In the context of |owm|, biological objects are classes of, for instance, anatomical features of a worm. That is to say, statements made about C. elegans are not about a specific worm, but are stated about the entire class of worms. The semantics of a ``property SimpleProperty/value value`` triple are that if any value is set, then without any additional statements being made, an instance of the object has been observed to have the value at some point in time, somewhere, under some set of conditions. In other words, the statement is an existential quantification over the associated object(class).

The purpose of the identifiers for Properties is to allow statements to be made about them directly. An example::

    <http://openworm.org/entities/Entity/1> <http://openworm.org/entities/Entity/interactsWith> <http://openworm.org/entities/Entity_interactsWith/2> .
    <http://openworm.org/entities/Entity_interactsWith/2> <http://openworm.org/entities/SimpleProperty/value> <http://openworm.org/entities/Entity/3> .

    <http://openworm.org/entities/Entity/4> <http://openworm.org/entities/Entity/modulates> <http://openworm.org/entities/Entity_modulates/5> .
    <http://openworm.org/entities/Entity_modulates/5> <http://openworm.org/entities/SimpleProperty/value> <http://openworm.org/entities/Entity_interactsWith/2>


RDF structure for |owm|
=======================

For most use cases, it is (hopefully) not necessary to write custom queries over the RDF graph in order to work with |owm|. However, if it does become necessary, it will be helpful to have an understanding of the structure of the RDF graph. Thus, a summary is given below.

For all :class:`DataObjects <.DataObject>` which are not :class:`Properties <.Property>`, there is an identifier of the form

::

    <http://openworm.org/entities/Object_type/md5sum>

stored in the graph. This identifier will be associated with type data::

    <http://openworm.org/entities/Object_type/md5sum> rdf:type <http://openworm.org/entities/Object_type> .
    <http://openworm.org/entities/Object_type/md5sum> rdf:type <http://openworm.org/entities/parent_of_Object_type> .
    <http://openworm.org/entities/Object_type/md5sum> rdf:type <http://openworm.org/entities/parent_of_parent_of_Object_type> .
    ...

Properties have a slightly different form. They also have an identifier, which for :class:`SimpleProperties <.SimpleProperty>` will look like this::

    <http://openworm.org/entities/OwnerType_propertyName/md5sum>

``OwnerType`` is the type of the Property's owner and ``propertyName`` is the name by which the property is accessed from an object of the owner's type. Other Properties will not necessarily have this form, but all of the standard Properties are implemented in terms of SimpleProperties and have no direct representation in the graph. For other Properties it is necessary to refer to their documentation or to examine the triples released by the Property of interest.

A DataObject's identifier is connected to a property in a triple like::

    <http://openworm.org/entities/OwnerType/md5sum> <http://openworm.org/entities/OwnerType/propertyName> <http://openworm.org/entities/OwnerType_propertyName/md5sum>

and the property is connected to its values like::

    <http://openworm.org/entities/OwnerType_propertyName/md5sum> <http://openworm.org/entities/SimpleProperty/value> "A literal value"
