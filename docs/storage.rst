.. _storage:

Data Storage
============

PyOpenWorm data storage is based around the idea of local databases with of RDF
triples where data is shared between local databases by uploading and downloading
serializations of `RDF named graphs`_ (from here on, just "graphs") from/to
shared servers. This upload/download of graphs is not done synchronously: the
uploader publishes a set of graphs and then, at some later time, a downloader
can retrieve the graphs. An important point here is that a *set* of graphs is
published, rather than a single graph. PyOpenWorm encourages and rewards the
division of graphs according to the who, what, when, and why of the statements
they represent (see :ref:`contexts` for more). Once we separate these contexts,
however, we need a way to combine them together, and we do that with "imports"
statements of the form ``:graphA Context:imports :graphB``. 

.. _RDF named graphs: https://en.wikipedia.org/wiki/Named_graph

The exact method for upload/download can
vary, but the choice of which method to use is the result of a selection process
controlled by the requester of the graph (see :ref:`graph_access_selection`, below).

.. _graph_access_selection:

Graph Access Selection
----------------------
