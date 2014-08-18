.. _sharing:

Sharing Data with other users 
------------------------------

Sharing is key to |pow|. This document covers the appropriate way to share changes with other |pow| users.

The shared |pow| database is stored in a Git repository distinct from the |pow| source code. Currently the database is stored [[somewhere]].

When you create a database normally, it will be stored in a format which is opaque to humans. In order to share your database you have two options: You can share the scripts which are used to create your database or you can share a human-readable serialization of the database. The second option is better since it doesn't require re-running your script to use the generated data, but it is best to share both. 

For sharing the serialization, we prefer the n3 format::
    
  import PyOpenWorm as P
  P.config()['rdf.graph'].serialize('out.n3', format='n3')

add the file to a git repository, commit, and submit a pull request on the shared repo.
