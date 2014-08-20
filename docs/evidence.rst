.. _evidence:

Metadata in PyOpenWorm
======================

Attaching evidence
-------------------
Attaching evidence to an object is as easy as::

      e = Evidence(author='White et al.', date='1986')
      e.asserts(Connection(pre_cell="VA11", post_cell="VD12"))
      e.save()

But what does this series of statements mean? For us it means that White et al. assert that "the cells VA11 and VD12 have a connection". 
In particular, it says nothing about the neurons themselves.

Another example::

      e = Evidence(author='Sulston et al.', date='1983')
      e.asserts(Neuron(name="AVDL").lineageName("AB alaaapalr"))
      e.save()

This would say that Sulston et al. claimed that neuron AVDL has lineage AB alaaapalr.

Now a more ambiguous example::

      e = Evidence(author='Sulston et al.', date='1983')
      e.asserts(Neuron(name="AVDL"))
      e.save()

What might this mean? There's no clear relationship being discussed as in the previous examples. There are two reasonable semantics for
these statements. They could indicate that Sulston et al. assert everything about the AVDL (in this case, only its name). Or they could
indicate that Sulston et al. state the existence of AVDL. We will assume the semantics of the latter for *most* objects. The second
intention can be expressed as (TODO)::

      e = Evidence(author='Sulston et al.', date='1983')
      e.asserts_all_about(Neuron(name="AVDL"))
      e.save()

`asserts_all_about` individually asserts each of the properties of the Neuron including its existence. It does not recursively assert
properties of values set on the AVDL Neuron. If, for instance, the Neuron had a *complex object* as the value for its receptor types with
information about the receptor's name primary agonist, etc., `asserts_all_about` would say nothing about these. However, `asserts_all`::

      e.asserts_all(Neuron(name="AVDL",receptor=complex_receptor_object))

would make the aforementioned recursive statement. 

Retrieving evidence
-------------------

.. Not tested with the latest

Retrieving evidence for an object is trivial as well ::

      e = Evidence()
      e.asserts(Connection(pre_cell="VA11", post_cell="VD12"))
      for x in e.load():
         print x

This would print all of the evidence for the connection between VA11 and VD12

It's important to note that the considerations of recursive evidence assertions above do not operate for retrieval. Only evidence for the
particular object queried (the Connection in the example above), would be returned and not any evidence for anything otherwise about VA11 
or VD12.
