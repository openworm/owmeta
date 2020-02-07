.. _publishing_datasources:

Publishing DataSources
======================

:py:class:`~owmeta.datasource.DataSource` is a subclass of
:py:class:`~owmeta.dataobject.DataObject` with a few features to make
describing data files (CSV, HDF5, Excel) a bit more consistent and to make
recovering those files, and information about them, more reliable. In order to
have that reliability we have to take some extra measures when publishing a
``DataSource``. In particular, we must publish local files referred to by the
``DataSource`` and relativize those references. This file publication happens
in the :ref:`"deploy" phase <package_lifecycle_deploy_phase>` of the data
packaging lifecycle. Before that, however, a description of what files need to
be published is generated in the :ref:`"stage" phase
<package_lifecycle_stage_phase>`. In the "stage" phase, the ``DataSources``
with files needing publication are queried for in the configured triple store,
and the "staging manager", the component responsible for coordinating the
"stage" phase identifies file references that refer to the same files and
directories.
