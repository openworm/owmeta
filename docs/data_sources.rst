.. _data_sources:

|pow| Data Sources
==================

A Note on |pow| Data
--------------------
There are various different sources for *C. elegans* data
available, each with their own idiosyncrasies. To provide the most
accurate and up-to-date information in PyOpenWorm, some decisions had
to be made about which data sources should be used. In the interest of 
transparency and reproducibility, this page details the choices that went into
curating the various data sources that form the backbone of |pow|.

The database behind |pow| also has the ability to tag each fact with a
source using the `evidence module described here <process.html#provenance>`_.

Below, each major element of the worm's anatomy that |pow| stores data
on is considered individually. The data being used is tagged by source
in a superscript, and the decisions made during the curation process 
(if any) are described.

Neurons
-------

- Cell descriptions [2]_
- Innexins [1]_
- Lineage names [2]_
- Neuron names [1]_
- Neuron types [3]_
- Neuropeptides [1]_
- Neurotransmitters [1]_
- Receptors [1]_

Muscle cells
------------

- Cell descriptions [2]_
- Lineage names [2]_
- Muscle names [1]_
- Neurons that innervate each muscle [1]_

Connectome
----------

- Gap junctions [4]_
- Synapses [4]_

Curation note
^^^^^^^^^^^^^

There is another source of C. *elegans* connectome data that was created
by members of the OpenWorm project. The history of this spreadsheet is 
mostly contained in
`this forum post <https://groups.google.com/forum/#!topic/openworm-discuss/G9wKoR8N-l0/discussion>`_
We decided to use the WormAtlas spreadsheet [4]_ as the authoritative source
for connectome data, as it was not processed by members of OpenWorm, and
appears on a reference site (WormAtlas).

----------

Data Source References
----------------------

.. [1] `Tim Busbice's interactive database <http://www.interintelligence.org/openworm/>`_
.. [2] `WormAtlas Complete Cell List <http://www.wormatlas.org/celllist.htm>`_
.. [3] `C Elegans Neuronal Network Details <https://docs.google.com/spreadsheets/d/1Jc9pOJAce8DdcgkTgkUXafhsBQdrer2Y47zrHsxlqWg/edit#gid=2>`_
.. [4] `WormAtlas Connectivity Data <http://www.wormatlas.org/neuronalwiring.html#Connectivitydata>`_
