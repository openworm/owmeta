..cmd:

``pow`` Command Line
====================

The ``pow`` command line provides a high-level interface for working with
PyOpenWorm-managed data. The central object which ``pow`` works on is the
repository, which contains the database -- a set of files in binary format. The
sub-commands act on important files inside the repository or with entities in
the database.

To get usage information::
   
   pow --help

To clone a repository::

   pow clone $database_url

This will clone a repository into ``.pow`` in your current working directory.
After a successful clone, a binary database usable as a PyOpenWorm store will
have been created from the serialized graphs in the repository.

To save changes made to the database::

   pow commit -m "I'm a commit message!"

To recreate the database from serialized graphs, *including uncommited changes*::

   pow regendb

To make a new repository::

   pow init

This will create a repository in ``.pow`` in your current working directory.
