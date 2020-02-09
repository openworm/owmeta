.. _data_requirements:

Requirements for data storage in OpenWorm
=========================================
Our OpenWorm database captures facts about *C. elegans*. The database stores
data for generating model files and together with annotations describing the
origins of the data. Below are a set of recommendations for implementation of
the database organized around an |RDF| model.

Interface
---------
Access is through a Python library which communicates with the database. This
library serves the function of providing an object oriented view on the database
that can be accessed through the Python scripts commonly used in the project.
The :ref:`api <owm_module>` is described separately.

Data modeling
-------------
Biophysical and anatomical data are included in the database. A sketch of some
features of the data model is below. Also included in our model are the
relationships between these types. Given our choice of data types, we do not
model the individual interactions between cells as entities in the database.
Rather these are described by generic predicates in an `RDF triple`_.
For instance, neuron A synapsing with muscle cell B would give a statement
(A, synapsesWith, B), but A synapsing with neuron C would also have
(A, synapsesWith, C).

.. _RDF triple: http://stackoverflow.com/a/1122451

Nervous system
~~~~~~~~~~~~~~
For the worm's nervous system, we capture a few important data types (listed
`below <#datatypes>`__). These correspond primarily to the anatomical structures
and chemicals which are necessary for the worm to record external and internal
stimuli and activate its body in response to those stimuli.

.. _datatypes:

Data types
++++++++++
A non-exhaustive list of neurological data types in our C. elegans database:

- receptor types identified in the nerve cell
- neurons
- ion channels
- neurotransmitters
- muscle receptors

Development
~~~~~~~~~~~
*C. elegans* has very stable cell division patterns in the absence of
mutations. This means that we can capture divisions in our database as static
'daughterOf' relationships. The theory of differentiation codes additionally
gives an algorithmic description to the growth patterns of the worm which
describes signals transmitted between developing cells. In order to test this
theory we would like to leverage existing photographic data indicating the
volume of cells at the time of their division as this relates to the
differentiation code stored by the cell. Progress on this issue is documented
`on GitHub`_

.. _on Github: https://github.com/openworm/owmeta/issues/7#issuecomment-45401916

Aging
~~~~~
Concurrently with development, we would like to begin modeling the effects of aging on the
worm. Aging typically manifests in physiological changes due to transcription errors or
cell death. These physiological changes can be represented abstractly as parameters to the
function of biological entities. See `GitHub`_ for further discussion.

.. _Github: https://github.com/openworm/owmeta/issues/6

Information assurance
---------------------

Provenance
~~~~~~~~~~
Tracking the origins of facts stated in the database demands a method of annotating
statements in our database. Providing citations for facts must be as simple as providing a
global identifier (e.g., URI, DOI) or a local identifier (e.g., Bibtex identifier, Pubmed
ID). With owmeta, supporting information can be attached to `named graphs`_, which are
groupings of statements with a URI attached to them. A named graph can have as many or as
few statements as desired. Furthermore, a given triple can occur in multiple named graphs.
Further details for the attachment of evidence using this technique are given in the
:ref:`api <owm_module>`.

.. _named graphs: https://en.wikipedia.org/wiki/Named_graph

In line with current practices for communication through the source code management
platform, GitHub, we track responsibility for new uploads to the database through the
`OpenWormData`_ Git repository. Each named graph is canonicalized -- essentially, triples
are sorted and written to a text file -- and committed to a Git repository which gives us,
at least, an email address and a timestamp for all modifications.

.. _OpenWormData: https://github.com/openworm/OpenWormData

Access control
~~~~~~~~~~~~~~
Data in owmeta are distributed as a bundle, a packaging structure which contains a set of
canonicalized named graphs and, optionally, some files.  Responsibility for restricting
who can modify a bundle is, in the first instance, up to the bundle creator. When the
bundle is actually distributed, the responsibility then falls on the distributor to ensure
authentication of the bundle's provider and integrity of the bundle.

In OpenWorm, we create bundles from the OpenWormData GitHub repository. Access to the
repository is managed by senior OpenWorm contributors. Bundles are deployed to Google
Drive with write access controlled by Mark Watts. You can fetch OpenWorm bundles by adding
a remote like this::

    owm bundle remote add google-drive 'https://drive.google.com/uc?id=1NYAcKdcvoFu5c7Nz3l4hK5UacG_eD56V&authuser=0&export=download'

``google-drive`` can be substituted with any string.

Miscellaneous
-------------
Versioning
~~~~~~~~~~
Experimental methods are constantly improving in biological research. These improvements
may require updating the data we reference or store internally. However, in making updates
we must not immediately expunge older content, breaking links created by internal and
external agents. Instead, we utilize bundle versioning to track revisions to the data.
Each successive release of the bundle increments the bundle version number. 

Why RDF?
--------
|RDF| offers advantages in resilience to schema additions and increased
flexibility in integrating data from disparate sources. [1]_ These qualities can
be valued by comparison to relational database systems. Typically, schema
changes in a relational database require extensive work for applications using
it. [2]_ In the author's experience, RDF databases offer more freedom in
restructuring. Also, for data integration, SPARQL, the standard language for
querying over RDF has
`Federated queries <http://www.w3.org/TR/sparql11-federated-query/>`_ which
allow for nearly painless integration of external SPARQL endpoints with
existing queries.

.. [1] http://answers.semanticweb.com/questions/19183/advantages-of-rdf-over-relational-databases
.. [2] http://research.microsoft.com/pubs/118211/andy%20maule%20-%20thesis.pdf

.. XXX: Copy edit and transition

The advantage of local storage of the database that goes along with each copy
of the library is that the data will have the version number of the library.
This means that data can be 'deprecated' along with a deprecated version of the
library.  This also will prevent changes made to a volatile database that
break downstream code that uses the library.
