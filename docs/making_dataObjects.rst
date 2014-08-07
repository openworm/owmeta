.. _mkdobj:

Making data objects
====================
To make new objects like ``Neuron`` or ``Worm``, for the most part, you just need to make a Python class.
Say, for example, that I want to record some information about drug reactions in C. elegans. I make
``Drug`` and ``Experiment`` classes to describe C. elegans reactions::

    from PyOpenWorm import (DataObject,
                            DatatypeProperty,
                            ObjectProperty,
                            Worm,
                            Evidence,
                            connect)

    class Drug(DataObject):
        # We set up properties in __init__
        def __init__(self,drug_name=False,*args,**kwargs):
            # pass arguments to DataObject
            DataObject.__init__(self,*args,**kwargs)
            Drug.DatatypeProperty('name', owner=self)
            if drug_name:
                self.name(drug_name)

    class Experiment(DataObject):
        def __init__(self,*args,**kwargs):
            # pass arguments to DataObject
            DataObject.__init__(self,*args,**kwargs)
            Experiment.ObjectProperty('drug', value_type=Drug, owner=self)
            Experiment.ObjectProperty('subject', value_type=Worm, owner=self)
            Experiment.DatatypeProperty('route_of_entry', owner=self)
            Experiment.DatatypeProperty('reaction', owner=self)

    connect()
    # Set up with the RDF translation machinery
    Experiment.register()
    Drug.register()

I can then make a Drug object for moon rocks and describe an experiment by Aperture Labs::

    d = Drug('moon rocks')
    e = Experiment()
    w = Worm("C. elegans")
    ev = Evidence(author="Aperture Labs")
    e.subject(w)
    e.drug(d)
    e.route_of_entry('ingestion')
    e.reaction('no reaction')
    ev.asserts(e)

and save it::

    ev.save()

For simple objects, this is all we have to do.

You can also add properties to an object after it has been created by calling either ObjectProperty or DatatypeProperty on the object as is done in ``__init__``::

    d = Drug('moon rocks')
    Drug.DatatypeProperty('granularity', owner=self)
    d.granularity('ground up')

Properties added in this fashion will not propagate to any other objects, but they will be saved along with the object they are attached to.
