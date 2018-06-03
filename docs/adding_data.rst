.. _adding_data:

Adding Data to *YOUR* OpenWorm Database
========================================

So, you've got some biological data about the worm and you'd like to save it in
|pow|, but you don't know how it's done?

You've come to the right place!

A few biological entities (e.g., Cell, Neuron, Muscle, Worm) are pre-coded into
|pow|. The full list is available in the :ref:`API <pow_module>`.
If these entities already cover your use-case, then all you need to do is add
values for the appropriate fields and save them. If you have data already loaded
into your database, then you can load objects from it::

    n = Neuron()
    n.receptor('UNC-13')
    for x in n.load():
        do_something_with_unc13_neuron(n)

If you need additional entities it's easy to create them. Documentation for this
is provided :ref:`here <making_dataObjects>`.

Typically, you'll want to attach the data that you insert to entities already in
the database. This allows you to recover objects in a hierarchical fashion from
the database later. ``Worm``, for instance has a property, ``neuron_network``,
which points to the ``Network`` which should contain all neural cells and
synaptic connections. To initialize the hierarchy you would do something like::

    ctx = Context(ident='http://example.org/c-briggsae')
    w = ctx(Worm)('C. briggsae') # The name is optional and currently defaults to 'C. elegans'
    nn = ctx(Network)()          # make a neuron network
    w.neuron_network(nn)         # attach to the worm the neuron network
    n = ctx(Neuron)()            # make an unnamed neuron
    n.receptor('UNC-13')         # state that the neuron has a UNC-13 type receptor
    nn.neuron(n)                 # attach to the neuron network
    ctx.save_context()           # save all of the data attached to the worm

It is possible to create objects without attaching them to anything and they can
still be referenced by calling load on an instance of the object's class as in
``n.load()`` above. This also points out another fact: you don't have to set up
the hierarchy for each insert in order for the objects to be linked to existing
entities. If you have previously set up connections to an entity (e.g.,
``Worm('C. briggsae')``), assuming you *only* have one such entity, you can
refer to things attached to it without respecifying the hierarchy for each
script. The database packaged with |pow| should have only one Worm and one
Network.

Remember that once you've set up all of the data, you must save the objects. For
now, this requires keeping track of top-level objects -- objects which aren't
values of some other property -- and calling ``save()`` on each of them
individually. This isn't too difficult to achieve.

Future capabilities:

* Adding propositional logic to support making statements about all entities
  matching some conditions without needing to ``load()`` and ``save()`` them
  from the database.
* Statements like::

    ctx = Context(ident='http://example.org/c-briggsae')
    w = ctx.stored(Worm)()
    w.neuron_network.neuron.receptor('UNC-13')
    l = list(w.load()) # Get a list of worms with neurons expressing 'UNC-13'

  currently, to do the equivalent, you must work backwards, finding all neurons
  with UNC-13 receptors, then getting all networks with those neurons, then
  getting all worms with those networks::

    worms = set()
    n = ctx.stored(Neuron)()
    n.receptor('UNC-13')
    for ns in n.load():
        nn = ctx.stored(Network)()
        nn.neuron(ns)
        for z in nn.load():
            w = ctx.stored(Worm)()
            w.neuron_network(z)
            worms.add(w)
    l = list(worms)

  It's not difficult logic, but it's 8 extra lines of code for a conceptually
  very simple query.

* Also, queries like::

    l = list(ctx.stored(Worm)('C. briggsae').neuron_network.neuron.receptor()) # get a list
    #of all receptors expressed in neurons of C. briggsae

  Again, not difficult to write out, but in this case it actually gives a much
  longer query time because additional values are queried in a ``load()`` call
  that are never returned.

  We'd also like operators for composing many such strings so::

    ctx.stored(Worm)('C. briggsae').neuron_network.neuron.get('receptor', 'innexin') # list
    #of (receptor, innexin) values for each neuron

  would be possible with one query and thus not requiring parsing and iterating
  over neurons twice--it's all done in a single, simple query.

Contexts
--------
Above, we didn't qualify our statements in any way, but stated them as simple
facts. In reality, our statements are made in a context that influences how
they should be interpreted. In |pow|, that context-sensitivity is modeled by
using :class:``Context`` objects. To see what this looks like, let's start with
an example.

Example 1
^^^^^^^^^
I have data about widgets from BigDataWarehouse (BDW) that I want to translate
into RDF using |pow|, but I don't want put them with my other widget data since
BDW data may conflict with mine. Also, if get more BDW data, I want to be able
to relate these data to that. A good way to keep data which are made at
distinct times or which come from different, possibly conflicting, sources is
using contexts. The code below shows how to do that::

    from rdflib import ConjunctiveGraph
    from PyOpenWorm.context import Context
    from mymod import Widget # my model for Widgets
    from bdw import Load # BigDataWarehouse API

    # Create a Context with an identifier appropriate to this BDW data import
    ctx = Context(ident='http://example.org/data/imports/BDW_Widgets_2017-2018')

    # Create a context manager using the default behavior of reading the
    # dictionary of current local variables
    with ctx(W=Widget) as c:
        for record in Load(data_set='Widgets2017-2018'):
            # declares Widgets in this context
            c.W(part_number=record.pnum,
                fullness=record.flns,
                hardiness=record.hrds)
    
    # Create an RDFLib graph as the target for the data
    g = ConjunctiveGraph()

    # Save the data
    c.save_context(g)

    # Serialize the data in the nquads format so we can see that all of our
    # statements are in the proper context
    print(g.serialize(format='nquads'))

If you've worked with lots of data before, this kind of pattern should be
familiar. You can see how, with later imports, you would follow the naming
scheme to create new contexts (e.g., ``http://example.org/data/imports/BDW_Widgets_2018-2019``).

.. Context metadata
.. Importing contexts
.. Evidence, DataSources, DataTranslators, Provenance and contexts

