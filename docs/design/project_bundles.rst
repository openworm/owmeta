.. _project_bundles:

Project Bundles
===============
Project bundles are:

* collections of contexts,
* and a set of mappings between project-scoped human-friendly names and context
  identifiers.

They solve the problem of contexts containing different statements having the
same identifier.

There are several ways we can get different contexts with the same identifier: 

* through revisions of a context over time, 
* by distinct groups using the same context identifier, 
* or by contexts being distributed with different variants (e.g., a full and an abridged version).

In solving this problem of context ID aliasing, bundles also helps solve the
problem of having contexts with inconsistent statements in the same project by
providing a division within a project, between groups of contexts that aren't
necessarily related.

Relationships
-------------
Where not specified, the subject of a relationship can participate in the
relationship exactly once. For example, "A Dog has a Human", means "A Dog has
one and only one Human"

* A Project can have zero or more Bundles
* A Bundle can belong to only one Project
* A Human-Friendly Name is associated with a Content-Based Identifier
* A Content-Based Identifier has one or more Hashes
* A Hash can appear in zero or more Content-Based Identifiers
* A Hash has an Algorithm ID and a Message Digest
* A Content-Based Identifier has an optional Tag
* There is at most one Content-Based Identifier for a given Tag

Types
-----
A Tag is an arbitrary string
A Message Digest is a Base-64 encoding of a string of bytes

