.. _command:

``owm`` Command Line
====================

The ``owm`` command line provides a high-level interface for working with
owmeta-managed data. The central object which ``owm`` works on is the
repository, which contains the triple store -- a set of files in a binary
format.  The sub-commands act on important files inside the repository or with
entities in the database.

To get usage information::
   
   owm --help

To clone a repository::

   owm clone $database_url

This will clone a repository into ``.owm`` in your current working directory.
After a successful clone, a binary database usable as a owmeta store will
have been created from the serialized graphs in the repository.

To save changes made to the database::

   owm commit -m "I'm a commit message!"

To recreate the database from serialized graphs, *including uncommited changes*::

   owm regendb

To make a new repository::

   owm init

This will create a repository in ``.owm`` in your current working directory.


