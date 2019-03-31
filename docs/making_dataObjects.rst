.. _making_dataObjects:

Making data objects
====================
To make a new object type like :py:class:`~PyOpenWorm.neuron.Neuron` or
:py:class:`PyOpenWorm.worm.Worm`, for the most part, you just need to make a
Python class.

Say, for example, that I want to record some information about drug reactions
in C. elegans. I make ``Drug`` and ``Experiment`` classes to describe C.
elegans reactions::

    >>> from PyOpenWorm.dataObject import (DataObject,
    ...                                    DatatypeProperty,
    ...                                    ObjectProperty,
    ...                                    Alias)
    >>> from PyOpenWorm.worm import Worm
    >>> from PyOpenWorm.evidence import Evidence
    >>> from PyOpenWorm.document import Document
    >>> from PyOpenWorm.context import Context
    >>> from PyOpenWorm.mapper import Mapper
    >>> from PyOpenWorm import connect, ModuleRecorder

    >>> class Drug(DataObject):
    ...     name = DatatypeProperty()
    ...     drug_name = Alias(name)
    ...     def identifier_augment(self):
    ...         return self.make_identifier_direct(self.name.onedef())
    ...
    ...     def defined_augment(self):
    ...         return self.name.has_defined_value()
    
    >>> class Experiment(DataObject):
    ...     drug = ObjectProperty(value_type=Drug)
    ...     subject = ObjectProperty(value_type=Worm)
    ...     route_of_entry = DatatypeProperty()
    ...     reaction = DatatypeProperty()

    # Do some accounting stuff to register the classes. Usually happens behind
    # the scenes. 
    >>> m = Mapper(('PyOpenWorm.dataObject.DataObject',))
    >>> ModuleRecorder.add_listener(m)
    >>> m.process_classes(Drug, Experiment)

So, we have created I can then make a Drug object for moon rocks and describe an experiment by
Aperture Labs::

    >>> ctx = Context(ident='http://example.org/experiments', mapper=m)
    >>> d = ctx(Drug)(name='moon rocks')
    >>> e = ctx(Experiment)(key='experiment001')
    >>> w = ctx(Worm)('C. elegans')
    >>> e.subject(w)
    PyOpenWorm.statement.Statement(...Context(.../experiments"))

    >>> e.drug(d)
    PyOpenWorm.statement.Statement(...)

    >>> e.route_of_entry('ingestion')
    PyOpenWorm.statement.Statement(...)

    >>> e.reaction('no reaction')
    PyOpenWorm.statement.Statement(...)

    >>> ev = Evidence(key='labresults', reference=Document(author="Aperture Labs"))
    >>> ev.supports(ctx)
    PyOpenWorm.statement.Statement(...)

and save those statements::

    >>> ctx.save()

For simple objects, this is all we have to do.

You can also add properties to an object after it has been created by calling
either ObjectProperty or DatatypeProperty on the class::

    >>> d = ctx(Drug)(name='moon rocks')
    >>> Drug.DatatypeProperty('granularity', owner=d)
    __main__.Drug_granularity(owner=Drug(ident=rdflib.term.URIRef(u'http://openworm.org/entities/Drug/moon%20rocks')))

    >>> d.granularity('ground up')
    PyOpenWorm.statement.Statement(...Context(.../experiments"))

    >>> do = Drug()

Properties added in this fashion will not propagate to any other objects::

    >>> do.granularity
    Traceback (most recent call last):
        ...
    AttributeError: 'Drug' object has no attribute 'granularity'


They will, however, be saved along with the object they are attached to.
