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

- Cell descriptions [1]_
- Lineage names [1]_
- Neuron names [2]_
- Neuron types [1]_
- Neurotransmitters [1]_

Muscle cells
------------

- Cell descriptions [1]_
- Lineage names [1]_
- Muscle names [2]_
- Neurons that innervate each muscle [3]_

Connectome
----------

- Gap junctions [3]_
- Synapses [3]_

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

.. [1] Altun, Z.F., Herndon, L.A., Wolkow, C.A., Crocker, C., Lints, R. and Hall, D. H. (2015). WormAtlas. Retrieved from http://www.wormatlas.org
        - `WormAtlas Complete Cell List <http://www.wormatlas.org/celllist.htm>`_
.. [2] - Harris, T. W., Antoshechkin, I., Bieri, T., Blasiar, D., Chan, J., Chen, W. J., … Sternberg, P. W. (2010). WormBase: a comprehensive resource for nematode research. Nucleic Acids Research, 38(Database issue), D463–7. http://doi.org/10.1093/nar/gkp952
        - Lee, R. Y. N., & Sternberg, P. W. (2003). Building a cell and anatomy ontology of Caenorhabditis elegans. Comparative and Functional Genomics, 4(1), 121–6. http://doi.org/10.1002/cfg.248
.. [3] Emmons, S., Cook, S., Jarrell, T., Wang, Y., Yakolev, M., Nguyen, K., Hall, D. Whole-animal C. elegans connectomes.  C. Elegans Meeting 2015 http://abstracts.genetics-gsa.org/cgi-bin/celegans15s/wsrch15.pl?author=emmons&sort=ptimes&sbutton=Detail&absno=155110844&sid=668862
