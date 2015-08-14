.. _data_sources:

|pow| Data Sources
==================

The sources of data for PyOpenWorm are stored under the `OpenWormData/aux_data 
directory <https://github.com/openworm/PyOpenWorm/tree/5cc3042b004f167dbf18acc119474ea48b47810d/OpenWormData/aux_data>`_.  
These data sources are brought into PyOpenWorm by means of the 
`insert_worm.py script <https://github.com/openworm/PyOpenWorm/blob/5cc3042b004f167dbf18acc119474ea48b47810d/OpenWormData/scripts/insert_worm.py>`_, which shows exactly how a given kind of data is 
brought into the system.  For example `this method <https://github.com/openworm/PyOpenWorm/blob/5cc3042b004f167dbf18acc119474ea48b47810d/OpenWormData/scripts/insert_worm.py#L37>`_ shows where data about muscles 
comes from, while `this method <https://github.com/openworm/PyOpenWorm/blob/5cc3042b004f167dbf18acc119474ea48b47810d/OpenWormData/scripts/insert_worm.py#L218>`_ shows where the connectivity data comes from.  
A more detailed human readable key is provided below.


A Note on |pow| Data
--------------------
Below, each major element of the worm's anatomy that |pow| stores data
on is considered individually. The data being used is tagged by source
in a superscript, and the decisions made during the curation process 
(if any) are described.

Neurons
-------

- Cell descriptions [2]_
- Lineage names [2]_
- Neuron names [5]_
- Neuron types [3]_
- Neurotransmitters [8]_

Muscle cells
------------

- Cell descriptions [2]_
- Lineage names [2]_
- Muscle names [5]_
- Neurons that innervate each muscle [6]_

Connectome
----------

- Gap junctions [6]_
- Synapses [6]_

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

.. [2] `WormAtlas Complete Cell List <http://www.wormatlas.org/celllist.htm>`_
.. [3] `C Elegans Neuronal Network Details <https://docs.google.com/spreadsheets/d/1Jc9pOJAce8DdcgkTgkUXafhsBQdrer2Y47zrHsxlqWg/edit#gid=2>`_
.. [5] [Citation for Wormbase]
.. [6] [Steve Cook new data citation]
.. [7] [Extra Inferred Neurotransmitters: Shterionov, Janssens - 2011 paper citation][link to the neurotransmitters spreadsheet directly] -- starting point was an old connectome with unknown starting assumptions about neurotransmitters / receptors that need to be verified
.. [8] [Few, conservative neurotransmitters: C. Elegans II http://www.ncbi.nlm.nih.gov/books/NBK20175/]
