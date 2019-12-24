.. _project_distribution:

Project Distribution
====================
Projects are distributed as :ref:`bundle <project_bundles>` archives, 
also referred to as `dists` (short for distributions) in the documentation and
commands. The layout of files in a dist is largely the same as the format of a
``.owm`` directory on initial clone. In other words the bundle contains a set
of serialized graphs, an index of those graphs, an optional set of non-RDF data
that accompanies data sources stored amongst the graphs, and a configuration
file which serves as a working owmeta configuration file and a place for
metadata about the bundle. The archive file format can be allowed to vary,
between producers and consumers of dists, but at least the `.tar.gz` format
should be supported by general-purpose clients.

