.. _contexts:

Working with contexts
=====================
Contexts are introduced in :ref:`adding_data`. Here we provide a little
more...context.

Background
----------
Contexts were introduced to owmeta as a generic tool for grouping statements.
We need to group statements to make statements about statements like "Who made
these statements?" or "When were these statements made?". That's the main
usage. Beyond that, we need a way to share statements. Contexts have
identifiers by which we can naturally refer to contexts from other contexts.

owmeta needs a way to represent contexts with the existing statement form. Other
alternatives were considered, such as using Python's context managers, but I
(Mark) also wanted a way to put statements in a context that could also be
carried with the subject of the statement. Using the `wrapt <wrapt_>`_
package's proxies allows to achieve this while keeping the interface of the
wrapped object the same, which is useful since it doesn't require a user of the
object to know anything about contexts unless they need to change the context
of a statement.

.. _wrapt: https://wrapt.readthedocs.io/en/latest/

The remainder of this page will go into doing some useful things with contexts.

Classes and contexts
--------------------
owmeta can load classes as well as instances from an RDF graph. The packages which
define the classes must already be installed in the Python library path, and a
few statements need to be in the graph you are loading from or in a graph
imported (transitively) by that graph. The statements you need are these

.. code-block:: turtle

   :a_class_desc <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://openworm.org/entities/PythonClassDescription> .
   :a_class_desc <http://openworm.org/entities/ClassDescription/module> :a_module .
   :a_class_desc <http://openworm.org/entities/PythonClassDescription/name> "AClassName" .

   :a_module <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://openworm.org/entities/PythonModule> .
   :a_module <http://openworm.org/entities/PythonModule/name> "APackage.and.module.name" .

where ``:a_class_desc`` and ``:a_module`` are placeholders for objects which
will typically be created by owmeta on the user's behalf, and ``AClassName`` is
the name of the class available at the top-level of the module
``APackage.and.module.name``. These statements will be created in memory by
owmeta when a module defining a
:py:class:`~owmeta.dataObject.DataObject`-derived class is first processed by a
:py:class:`~owmeta.mapper.Mapper` which will happen after the module is
imported.

Query Performance
-------------------
With the default "lazy_pickle" storage, access on within a context is
preferred over access between contexts. This means that if you want to query
within a set of statements, it is helpful to put them in as single context
