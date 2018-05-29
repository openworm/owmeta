.. _data_sources:

|pow| Data Sources
==================

The sources of data for PyOpenWorm are stored under the `OpenWormData/aux_data
directory <https://github.com/openworm/PyOpenWorm/tree/5cc3042b004f167dbf18acc119474ea48b47810d/OpenWormData/aux_data>`_.

These data sources are brought into PyOpenWorm by means of the `insert_worm.py script`_, which shows exactly how a given
kind of data is brought into the system.  For example `this method <m1_>`_ shows where data about muscles comes from,
while `this method <m2_>`_ shows where the connectivity data comes from. A more detailed human readable key is provided
below.

.. _insert_worm.py script: https://github.com/openworm/PyOpenWorm/blob/5cc3042b004f167dbf18acc119474ea48b47810d/OpenWormData/scripts/insert_worm.py
.. _m1: https://github.com/openworm/PyOpenWorm/blob/5cc3042b004f167dbf18acc119474ea48b47810d/OpenWormData/scripts/insert_worm.py#L37
.. _m2: https://github.com/openworm/PyOpenWorm/blob/5cc3042b004f167dbf18acc119474ea48b47810d/OpenWormData/scripts/insert_worm.py#L218

A Note on |pow| Data
--------------------
Below, each major element of the worm's anatomy that |pow| stores data
on is considered individually. The data being used is tagged by source
in a superscript, and the decisions made during the curation process
(if any) are described.

Neurons
-------

- Neuron names [2]_: Extracted from WormBase.  Dynamic version on `this google spreadsheet <gs1_>`_.  Staged in `this csv file <csv2_>`_.  Parsed by `this method <m3_>`_.
- Neuron types [1]_: Extracted from WormAtlas.org.  Staged in `this csv file <csv1_>`_.  Parsed by `this method <m4_>`_.
- Cell descriptions [1]_: Extracted from WormAtlas.org.  Staged in `this tsv file <tsv1_>`_.  Parsed by `this method <m5_>`_.
- Lineage names [1]_: Extracted from WormAtlas.org.  Dynamic version on `this google spreadsheet <gs2_>`_.  Staged in `this tsv file <tsv1_>`_.  Parsed by `this method <m5_>`_.
- Neurotransmitters [1]_: Extracted from WormAtlas.org.  Dynamic version on `this google spreadsheet <gs2_>`_.  Staged in `this csv file <csv1_>`_.  Parsed by `this method <m7_>`_.
- Neuropeptides [1]_: Extracted from WormAtlas.org.  Dynamic version on `this google spreadsheet <gs2_>`_.  Staged in `this csv file <csv1_>`_.  Parsed by `this method <m8_>`_.
- Receptors [1]_: Extracted from WormAtlas.org.  Dynamic version on `this google spreadsheet <gs2_>`_.  Staged in `this csv file <csv1_>`_.  Parsed by `this method <m9_>`_.
- Innexins [1]_: Extracted from WormAtlas.org.  Dynamic version on `this google spreadsheet <gs2_>`_.  Staged in `this csv file <csv1_>`_.  Parsed by `this method <m10_>`_.

.. _gs1: https://docs.google.com/spreadsheets/d/1NDx9LRF_B2phR5w4HlEtxJzxx1ZIPT2gA0ZmNmozjos/edit#gid=1
.. _gs2: https://docs.google.com/spreadsheets/d/1Jc9pOJAce8DdcgkTgkUXafhsBQdrer2Y47zrHsxlqWg/edit
.. _m3: https://github.com/openworm/PyOpenWorm/blob/945f7172f0dff1d022ce0574f3c630ee53297386/OpenWormData/scripts/insert_worm.py#L145
.. _m4: https://github.com/openworm/PyOpenWorm/blob/945f7172f0dff1d022ce0574f3c630ee53297386/OpenWormData/scripts/insert_worm.py#L287
.. _m5: https://github.com/openworm/PyOpenWorm/blob/945f7172f0dff1d022ce0574f3c630ee53297386/OpenWormData/scripts/insert_worm.py#L68
.. _m7: https://github.com/openworm/PyOpenWorm/blob/945f7172f0dff1d022ce0574f3c630ee53297386/OpenWormData/scripts/insert_worm.py#L262
.. _m8: https://github.com/openworm/PyOpenWorm/blob/945f7172f0dff1d022ce0574f3c630ee53297386/OpenWormData/scripts/insert_worm.py#L274
.. _m9: https://github.com/openworm/PyOpenWorm/blob/945f7172f0dff1d022ce0574f3c630ee53297386/OpenWormData/scripts/insert_worm.py#L280
.. _m10: https://github.com/openworm/PyOpenWorm/blob/945f7172f0dff1d022ce0574f3c630ee53297386/OpenWormData/scripts/insert_worm.py#L268
.. _csv1: https://github.com/openworm/PyOpenWorm/blob/945f7172f0dff1d022ce0574f3c630ee53297386/OpenWormData/aux_data/Modified%20celegans%20db%20dump.csv
.. _csv2: https://github.com/openworm/PyOpenWorm/blob/945f7172f0dff1d022ce0574f3c630ee53297386/OpenWormData/aux_data/C.%20elegans%20Cell%20List%20-%20WormBase.csv
.. _tsv1: https://github.com/openworm/PyOpenWorm/blob/945f7172f0dff1d022ce0574f3c630ee53297386/OpenWormData/aux_data/C.%20elegans%20Cell%20List%20-%20WormAtlas.tsv

Gene expression data below, additional to that extracted from WormAtlas concerning receptors, neuropeptides, neurotransmitters and innexins are parsed by `this method <https://github.com/openworm/PyOpenWorm/blob/4eb25df267ce385053f746ceb66e74d9c616403f/OpenWormData/scripts/insert_worm.py#L217>`_:

- Monoamine secretors and receptors, neuropeptide secretors and receptors [4]_: Dynamic version on `this google spreadsheet <https://docs.google.com/spreadsheets/d/1kCxOOKu1wAREa9VbBiWVVHh-GEC3kJk0A3YVEipPKcc/edit#gid=0>`_. Staged in `this csv file <https://github.com/openworm/PyOpenWorm/blob/27647748981fe0fe135b8aa39191c0e32579c923/OpenWormData/aux_data/expression_data/Bentley_et_al_2016_expression.csv>`_.

Muscle cells
------------

- Muscle names [2]_: Extracted from WormBase.  Dynamic version on `this google spreadsheet <gs1_>`_.  Staged in `this csv file <csv2_>`_.  Parsed by `this method <m11_>`_.
- Cell descriptions [1]_: Extracted from WormAtlas.org.  Dynamic version on `this google spreadsheet <gs2_>`_.  Staged in `this tsv file <tsv1_>`_.  Parsed by `this method <m5_>`_.
- Lineage names [1]_: Extracted from WormAtlas.org.  Dynamic version on `this google spreadsheet <gs2_>`_.  Staged in `this tsv file <tsv1_>`_.  Parsed by `this method <m5_>`_.
- Neurons that innervate each muscle [3]_: Extracted from data personally communicated by S. Cook.  Staged in `this csv file <csv3_>`_.  Parsed by `this method <m12_>`_.

.. _csv3: https://github.com/openworm/PyOpenWorm/blob/945f7172f0dff1d022ce0574f3c630ee53297386/OpenWormData/aux_data/herm_full_edgelist.csv
.. _m11: https://github.com/openworm/PyOpenWorm/blob/945f7172f0dff1d022ce0574f3c630ee53297386/OpenWormData/scripts/insert_worm.py#L44
.. _m12: https://github.com/openworm/PyOpenWorm/blob/945f7172f0dff1d022ce0574f3c630ee53297386/OpenWormData/scripts/insert_worm.py#L432

Connectome
----------

- Gap junctions between neurons [3]_: Extracted from data personally communicated by S. Cook.  Staged in `this csv file <csv3_>`_.  Parsed by `this method <m13_>`_.
- Synapses between neurons [3]_: Extracted from data personally communicated by S. Cook.  Staged in `this csv file <csv3_>`_.  Parsed by `this method <m13_>`_.

.. _m13: https://github.com/openworm/PyOpenWorm/blob/945f7172f0dff1d022ce0574f3c630ee53297386/OpenWormData/scripts/insert_worm.py#L423

Curation note
^^^^^^^^^^^^^

There was another source of C. *elegans* connectome data that was created
by members of the OpenWorm project that has since been retired. The history of this spreadsheet is
mostly contained in
`this forum post <https://groups.google.com/forum/#!topic/openworm-discuss/G9wKoR8N-l0/discussion>`_
We decided to use the Emmons data set [3]_ as the authoritative source
for connectome data, as it is the very latest version and updated version of the C. *elegans* connectome that we are familiar with.

----------

Data Source References
----------------------

.. [1] Altun, Z.F., Herndon, L.A., Wolkow, C.A., Crocker, C., Lints, R. and Hall, D. H. (2015). WormAtlas. Retrieved from http://www.wormatlas.org
        - `WormAtlas Complete Cell List <http://www.wormatlas.org/celllist.htm>`_
.. [2] - Harris, T. W., Antoshechkin, I., Bieri, T., Blasiar, D., Chan, J., Chen, W. J., … Sternberg, P. W. (2010). WormBase: a comprehensive resource for nematode research. Nucleic Acids Research, 38(Database issue), D463–7. http://doi.org/10.1093/nar/gkp952
        - Lee, R. Y. N., & Sternberg, P. W. (2003). Building a cell and anatomy ontology of Caenorhabditis elegans. Comparative and Functional Genomics, 4(1), 121–6. http://doi.org/10.1002/cfg.248
.. [3] Emmons, S., Cook, S., Jarrell, T., Wang, Y., Yakolev, M., Nguyen, K., Hall, D. Whole-animal C. elegans connectomes.  C. Elegans Meeting 2015 http://abstracts.genetics-gsa.org/cgi-bin/celegans15s/wsrch15.pl?author=emmons&sort=ptimes&sbutton=Detail&absno=155110844&sid=668862
.. [4] Bentley B., Branicky R., Barnes C. L., Chew Y. L., Yemini E., Bullmore E. T., Vertes P. E., Schafer W. R. (2016) The Multilayer Connectome of Caenorhabditis elegans. PLoS Comput Biol 12(12): e1005283. http://doi.org/10.1371/journal.pcbi.1005283
