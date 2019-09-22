.. _sharing:

Sharing Data with other users 
==============================

Sharing is key to |owm|. This document covers the appropriate way to share changes with other |owm| users.

The shared |owm| database is stored in a Git repository distinct from the |owm| source code. Currently the database is stored in a Github repository `here <https://github.com/mwatts15/OpenWormData>`_ .

When you create a database normally, it will be stored in a format which is opaque to humans. In order to share your database you have two options: You can share the scripts which are used to create your database or you can share a human-readable serialization of the database. The second option is better since it doesn't require re-running your script to use the generated data, but it is best to share both.

For sharing the serialization, you should first `clone <http://git-scm.com/book/en/Git-Basics-Getting-a-Git-Repository#Cloning-an-Existing-Repository>`_ the repository linked above, read the current serialization into your database (see `below <#loading>`_ for an example of how you would do this), and then write out the serialization::
    
  import owmeta as P
  P.connect('path/to/your/config/file')
  P.config()['rdf.graph'].serialize('out.n3', format='n3')
  P.disconnect()

.. _loading:

Commit, your changes to the git repository, push to a `fork <https://help.github.com/articles/fork-a-repo>`_ of the repository on Github and submit a `pull request <https://help.github.com/articles/using-pull-requests>`_ on the main repository. If for some reason your are unwilling or unable to create a Github account, post to the `OpenWorm-discuss <https://groups.google.com/forum/#!forum/openworm-discuss>`_ mailing list with a patch on the main repository with your changes and someone will have a look, possibly ask for adjustments or justification for your addition, and ultimately merge the changes for you.

To read the database back in you would do something like::
    
  import owmeta as P
  P.connect('path/to/your/config/file')
  P.config()['rdf.graph'].parse('out.n3', format='n3')
  P.disconnect()

Scripts are also added to the repository on Github to the :file:`scripts` subdirectory.
