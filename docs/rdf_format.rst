.. _rdf_format:

RDF structure for |pow|
=======================

For most use cases, it is (hopefully) not necessary to write custom queries over the RDF graph in order to work with |pow|. However, if it does become necessary it will be helpful to have an understanding of the structure of the RDF graph. Thus, a summary is given below.

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

The purpose of the identifiers for Properties is to allow statements to be made about them directly. An example::

    <http://openworm.org/entities/Entity/1> <http://openworm.org/entities/Entity/interactsWith> <http://openworm.org/entities/Entity_interactsWith/2> .
    <http://openworm.org/entities/Entity_interactsWith/2> <http://openworm.org/entities/SimpleProperty/value> <http://openworm.org/entities/Entity/3> .

    <http://openworm.org/entities/Entity/4> <http://openworm.org/entities/Entity/modulates> <http://openworm.org/entities/Entity_modulates/5> .
    <http://openworm.org/entities/Entity_modulates/5> <http://openworm.org/entities/SimpleProperty/value> <http://openworm.org/entities/Entity_interactsWith/2>
