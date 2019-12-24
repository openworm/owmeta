.. markw: Some of this has been done and some not: it is written as if it is
   the all done to avoid confusing changes in verb tense while the
   implementation is underway
.. _project_bundles:

Project Bundles
===============
A project bundle is composed of:

* a universally unique identifier,
* a version number,
* a collection of contexts,
* a distinguished "imports" context describing relationships between contexts,
  both those in the bundle, and between contexts in the bundle and in
  dependencies,

plus several optional components:

* a human-friendly name,
* a description of the bundle's contents,
* a collection of files,
* a listing of dependencies on other bundles, 
* a set of mappings between project-scoped identifiers and universal
  context identifiers.

They solve the problem of contexts containing different statements having the
same identifier for different purposes.

There are several ways we can get different contexts with the same identifier: 

* through revisions of a context over time, 
* by distinct groups using the same context identifier, 
* or by contexts being distributed with different variants (e.g., a full and an
  abridged version).

In solving this problem of context ID aliasing, bundles also helps solve the
problem of having contexts with inconsistent statements in the same project by
providing a division within a project, between groups of contexts that aren't
necessarily related.

Dependencies
------------
A bundle can declare other bundles upon which it depends, by listing those
other bundles identifiers and version numbers. In addition, a bundle can
declare contexts and files within the dependency that should be included or
excluded. More interestingly, a dependency specification may declare that
contexts declared within the dependency be renamed according to a number of
rewrite rules. This is to allow for using bundles with conflicting Context
Identifiers. 

Certain problems come up when dealing with contexts across different bundles.
This rewriting allows to keep separate the contexts in one bundle from another
and to prevent contexts with the same ID from conflicting with one another just
because they're brought in by a transitive dependency.

.. This doesn't solve the problem of conflicting versions of software packages
   referred to by the bundles. Need to make a good solution to that.

An example
``````````
This example describes a likely naming conflict that can arise in context
naming between bundles.

Bundles ``α``, ``β``, and ``γ``. With dependencies like so::

   α -> β -> γ

where both ``α`` and ``γ`` contain a context with ID ``c``. The dependency
resolution system will find the ``c`` context in ``γ`` and if there is no
remapping that removes the conflict, either in ``β`` or in ``α``, then the
system will deliver a message indicating that the context needs to be
deconflicted and in which bundle each of the conflicting declarations is. At
this point, the maintainer of the ``α`` package can make the change to omit
``c`` from ``γ``, omit it from ``α``, rename ``c`` in ``γ``, or rename it in
``α``. One special case, where ``α``'s ``c`` and ``γ``'s ``c`` are identical,
permits an automatic resolution; nonetheless, the system emits a warning in
this case, with the option to fail similarly to the case where the contexts are
distinct.
 
.. markw: There may also be a "merge" option which allows to combine the two
   versions of ``c``, but except for the case where the contexts are exactly
   identical (as discussed above), this requires an awareness of the logical
   meaning of statements within a context, which is more appropriately handled
   in the imports context.


Core bundles
------------
The "core" bundle contains (or depends on) metadata of all of the core classes
in owmeta which are needed to make owmeta features work. The core bundle is
generated automatically for whichever version of owmeta is in use and a
reference to it is added automatically when a bundle is installed. A given
bundle may, however, explicitly use a specific version of the core bundle.

Relationships
-------------
Where not specified, the subject of a relationship can participate in the
relationship exactly once. For example, "A Dog has a Human", means "A Dog has
one and only one Human".

* A Project can have zero or more Bundles
* A Bundle can belong to only one Project
* A Context Identifier is associated with one or more Content-Based Identifiers
* A Content-Based Identifier has a Hash
* A Content-Based Identifier has an RDF Serialization Format
* A Hash can appear in zero or more Content-Based Identifiers
* A Hash has an Algorithm ID and a Message Digest

.. XXX The content-based ID is lacks the RDF serialization in the first cut
   because there's only one we use. Will decide on format for representing the
   serialization format later, if we need it.

Types
-----
Below is a description in terms of lower-level types of some higher-level types
referenced above.

* A Message Digest is a Base-64 encoding of a string of bytes
* An Algorithm ID is a string that identifies an algorithm. Valid strings will
  be determined by any applications reading or writing the hashes, but in general
  will come from the set of constructors of Python's `hashlib` module.
* An RDF Serialization Format is a string naming the format of a canonical RDF
  graph serialization. Supported format strings:

  "nt"
     N-Triples
