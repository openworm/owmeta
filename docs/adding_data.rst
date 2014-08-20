.. _adding_data:

Adding Data to *YOUR* OpenWorm Database
========================================

So, you've got some biological data about the worm and you'd like to save it in |pow|,
but you don't know how it's done?

You've come to the right place!

A few biological entities (e.g., Cell, Neuron, Muscle, Worm) are pre-coded into |pow|. The full list is available in the :ref:`API <api>`.
If these entities already cover your use-case, then all you need to do is add values for the appropriate fields and save them. If you have data already loaded into your database, then you can load objects from it::

    n = Neuron()
    n.receptor('UNC-13')
    for x in n.load():
        do_something_with_unc13_neuron(n)

If you need additional entities it's easy to create them. Documentation for this is provided :ref:`here <making_dataObjects>`.

Typically, you'll want to attach the data that you insert to entities already in the database. This allows you to recover objects in a hierarchical fashion from the database later. ``Worm``, for instance has a property, ``neuron_network`` which points to the ``Network`` which should contain all neural cells and synaptic connections. To initialize the hiearchy you would do something like::

    w = Worm('C. briggsae') # The name is optional and currently defaults to 'C. elegans'
    nn = Network()          # make a neuron network
    w.neuron_network(nn)    # attach to the worm the neuron network
    n = Neuron()            # make an unamed neuron
    n.receptor('UNC-13')    # state that the neuron has a UNC-13 type receptor
    nn.neuron(n)            # attach to the neuron network
    w.save()                # save all of the data attached to the worm

It is possible to create objects without attaching them to anything and they can still be referenced by calling load on an instance of the object's class as in ``n.load()`` above. This also points out another fact: you don't have to set up the hierarchy for each insert in order for the objects to be linked to existing entities. If you have previously set up connections to an entity (e.g., ``Worm('C. briggsae')``), assuming you *only* have one such entity, you can refer to things attached to it without respecifying the hierarchy for each script. The database packaged with |pow| should have only one Worm and one Network.

Remember that once you've set up all of the data, you must save the objects. For now, this requires keeping track of top-level objects -- objects which aren't values of some other property -- and calling ``save()`` on each of them individually. This isn't too difficult to acheive

Future capabilities:

* Adding propositional logic to support making statements about all entities matching some conditions without needing to ``load()`` and ``save()`` them from the database.
* Statements like::

    w = Worm()
    w.neuron_network.neuron.receptor('UNC-13')
    l = list(w.load()) # Get a list of worms with neurons expressing 'UNC-13'

  currently, to do the equivalent, you must work backwards, finding all neurons with UNC-13 receptors, then getting all networks with those neurons, then getting all worms with those networks::

    worms = set()
    n = Neuron()
    n.receptor('UNC-13')
    for ns in n.load():
        nn = Network()
        nn.neuron(ns)
        for z in nn.load():
            w = Worm()
            w.neuron_network(z)
            worms.add(w)
    l = list(worms)

  It's not difficult logic, but it's 8 extra lines of code for a conceptually very simple query.
* Also, queries like::

    l = list(Worm('C. briggsae').neuron_network.neuron.receptor()) # get a list of all receptors expressed in neurons of C. briggsae

  Again, not difficult to write out, but in this case it actually gives a much longer query time because additional values are queried in a ``load()`` call that are never returned.
  We'd also like operators for composing many such strings so::

    Worm('C. briggsae').neuron_network.neuron.get('receptor', 'innexin') # list of (receptor, innexin) values for each neuron

  would be possible with one query and thus not requiring parsing and iterating over neurons twice--it's all done in a single, simple query.

