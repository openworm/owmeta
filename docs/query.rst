.. _query:

Querying for data objects
=========================

X.query form
------------
Creates modified version of the DataObject subclass which is fit for using in
queries.  May do other additional things latter, but, principally, it overrides
the identifier generation based on attributes.

Examples for querying for a :py:class:`~PyOpenWorm.neuron.Neuron` object::

   Neuron.query(name='AVAL')
   ctx(Neuron).query(name='AVAL')
   ctx.stored(Neuron).query(name='AVAL')
   ctx.mixed(Neuron).query(name='AVAL')

this can be important for when a class generates identifiers based on some
number of properties, but a subclass doesn't use the superclass identifier
scheme (:py:class:`~PyOpenWorm.cell.Cell` and Neuron are an example). The query
form allows to query from the superclass as you normally would to get
subclass instances.
