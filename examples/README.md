Some of these examples employ dummy database configurations just to demonstrate how to use the PyOpenWorm API.

To run others (those that connect with `default.conf`) you need to have a database set up.

To set up a database, you can run `init_db.py`. Examine that file to see how it works (there is also an example of creating the database in PyOpenWorm's main README).

*Note:* These examples assume that you are running them in the directory they're stored in

###Examples walkthrough

Before you get started with these examples, it would be good to read over [the main README](../README.md).

If this is your first time doing these examples, run `init_db.py` to set up a database for these examples.
This will take a minute of so to complete, so have a look at the script's comments while you're waiting.

#####1. `gap_junctions.py`

Here we select a neuron we are interested in and extract it from the database.
Whenever you want to get some data from the database, you need to connect to the database first.

As you can see in this script, when you connect to a database (*db*), you must use a configuration. For most purposes, you can just use `default.conf` to connect and not worry about it.

After connecting to the db you can grab the Worm object, and then the Network object. We place the Network in a variable `net`.

We can get a Neuron object by name now, so we decide to get 'AVAL'.

Now that we have the Neuron object, we can ask all sorts of questions about the neuron and get information back from the database.

In our example we get the number of Gap Junctions connecting AVAL with other neurons, but there are many more properties we could ask about.
Consult the Neuron API for a full list of properties.

#####2. `NeuronBasicInfo.py`

In this example, rather than querying about a single neuron, we iterate over the list of all Neuron objects in the network and classify them according to their `type()` property.

There is some usage of dictionaries and lists in this script, so if you are brand new to python check out something like [this](http://www.sthurlow.com/python/lesson06/) to get a grasp of what's going on.

#####3. `morpho.py`

Here we get another property of AVAL. Since we're starting a new script, we need to connect to the database again. 
In this example we are also *chaining* queries together to get what we want in fewer lines of code. 
Notice how we use `Worm().get_neuron_network().aneuron('AVAL')` to narrow our query from worm to network to single neuron (AVAL in this case).

This example also shows how you can get information about parts of the worm in non-text formats. In this case we get a neuroML morphology object for a particular cell, which could be used as input in another part of your pipeline

#####4. `add_reference.py`

This script shows how to create an Evidence object to assert some fact(s) about a DataObject in our db.
Every object on the Worm is a DataObject. This includes the Worm itself, individual Neurons, the Connections between them, the Neuron Network, everything.

Ideally, we would like everything we are storing in the db to be backed up by evidence, and an easy way to keep track of this is if we attach an Evidence object to things we have evidence for. 

In this example we make a temporary db and create a Neuron. We then make an Evidence object which includes links to the supporting "article". After this we use `e.asserts()` to link our Evidence with the fact that it supports.

Finally, we save our mock db and the evidence/neuron it contains.
