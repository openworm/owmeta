.. _data_requirements:

Requirements for data storage in OpenWorm
=========================================
Our OpenWorm database captures facts about C. `elegans`. The database stores
data for generating model files and together with annotations describing the
origins of the data. Below are a set of recommendations for implementation of
the database organized around an RDF model.

Interface
---------
Access is through a Python library which communicates with the database. This
library serves the function of providing an object oriented view on the database
that can be accessed through the Python scripts commonly used in the project.
The :ref:`api <owm_module>` is described separately.

Data modelling
--------------
Biophysical and anatomical data are included in the database. A sketch of some
features of the data model is below. Also included in our model are the
relationships between these types. Given our choice of data types, we do not
model the individual interactions between cells as entities in the database.
Rather these are described by generic predicates in an
`RDF triple <http://stackoverflow.com/a/1122451>`__.
For instance, neuron A synapsing with muscle cell B would give a statement
(A, synapsesWith, B), but A synapsing with neuron C would also have
(A, synapsesWith, C). Data which belong to the specific relationship between two
nodes is attached to an
`rdf:Statement object <http://www.w3.org/TR/rdf-schema/#ch_statement>`__
which points to the statement. This choice is intended to easy querying and
extension later on.

Nervous system
~~~~~~~~~~~~~~
In the worm's nervous system, we capture a few important data types (listed
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
Caenorhabditis elegans has very stable cell division patterns in the absence of
mutations. This means that we can capture divisions in our database as static
'daughter_of' relationships. The theory of differentiation codes additionally
gives an algorithmic description to the growth patterns of the worm which
describes signals transmitted between developing cells. In order to test this
theory we would like to leverage existing photographic data indicating the
volume of cells at the time of their division as this relates to the
differentiation code stored by the cell. Progress on this issue is documented
`on Github <https://github.com/openworm/owmeta/issues/7#issuecomment-45401916>`_.

Aging
~~~~~
Concurrently with development, we would like to begin modeling the effects of
aging on the worm. Aging typically manifests in physiological changes due to
transcription errors or cell death. These physiological changes can be
represented abstractly as parameters to the function of biological entities.
See `Github <https://github.com/openworm/owmeta/issues/6>`_ for further discussion.

Information assurance
---------------------

Reasoning and Data integrity
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
To make full use of RDF storage it's recommended to leverage reasoning over our
stored data. Encoding rules for the worm requires a good knowledge of both
C. elegans and the database schema. More research needs to be done on this going
forward. Preliminarily, SPIN, a constraint notation system based on SPARQL
looks like a good candidate for `specifying` rules, but an inference engine for
`enforcing` the rules still needs to be found.

Input validation
~~~~~~~~~~~~~~~~
Input validation is to be handled through the interface library referenced
`above <#interface>`_. In general, incorrect entry of biological names will
result in an error being reported identifying the offending entry and providing
a acceptable entries where appropriate. No direct access to the underlying data
store will be provided.

Provenance
~~~~~~~~~~
Tracking the origins of facts stated in the
database demands a method of annotating statements in our database. Providing
citations for facts must be as simple as providing a global identifier
(e.g., URI, DOI) or a local identifier (e.g., Bibtex identifier, Pubmed ID).
A technique called RDF reification allows us to annotate arbitrary facts in our
database with additional information. This technique allows for the addition of
structured citation data to facts in the database as well as annotations for
tracking responsibility for uploads to the database. Further details for the
attachment of evidence using this technique are given in the :ref:`api <owm_module>`.

In line with current practices for communication through the source code
management platform, Github, we would like to track responsibility for new
uploads to the database. Two methods are proposed for tracking this information:
RDF named graphs and RDF reification. Tracking information must include, at
least, a time-stamp on the update and linking of the submitted data to the
uploader's unique identifier (e.g., email address). Named graphs have the
advantage of wide support for the use of tracking uploads. The choice between
these depends largely the support of the chosen data store for named graphs.

Access control
~~~~~~~~~~~~~~~~~
Write access to data in the project has been inconsistent between various data
sources in the project. Going forward, write access to OpenWorm databases should
be restricted to authenticated users to forestall the possibility of malicious
tampering.

One way to accomplish this would be to leverage GitHub's fork and pull model
with the data as well as the code.  This would require two things:

- Instead of remote hosting of data, data is local to each copy of the library
  within a local database

- A serialization method dumps a new copy of the data out to a flat file
  enabling all users of the library to contribute their modifications to the data
  back to the owmeta project via GitHub.

A follow on to #2 is that the serialization method would need to preserve the
ordering of data elements and write in some plain text format so that a simple
diff on GitHub would be able to illuminate changes that were made.

Miscellaneous
-------------
Versioning
~~~~~~~~~~
Experimental methods are constantly improving in biological research. These
improvements may require updating the data we reference or store internally.
However, in making updates we must not immediately expunge older content,
breaking links created by internal and external agents. Ideally we would have a
means of deprecating old data and specifying replacements. On the level of single
resources, this is a trivial mapping which may be done transparently to all readers.
For a more significant change, altering the schema, human intervention may be
required to update external readers.

Why RDF?
---------
RDF offers advantages in resilience to schema additions and increased
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

FuXi
~~~~~~~~~~
`FuXi <https://github.com/RDFLib/FuXi>`_ is implemented as a semantic reasoning
layer in owmeta. In other words, it will be used to automatically infer (and
set) properties from other properties in the worm database.
This means that redundant information (ex: explicitly stating that each object
is of class "dataType") and subclass relationships (ex: that every object of
type "Neuron" is also of type "Cell"), as well as other relationships, can be
generated by the firing of FuXi's rule engine, without being hand-coded.

Aside from the time it saves in coding, FuXi may allow for a smaller footprint
in the cloud, as many relationships within the database could be inferred
*after* download.

A rule might be:

* { x is "Neuron" } => { x is "Cell" }

And a fact might be:

* { "ADLR" is "Neuron" }

Given the above rule and fact, FuXi could infer the new fact:

* { "ADLR" is "Cell" }


.. XXX: Copy edit and transition

The advantage of local storage of the database that goes along with each copy
of the library is that the data will have the version number of the library.
This means that data can be 'deprecated' along with a deprecated version of the
library.  This also will prevent changes made to a volatile database that
break downstream code that uses the library.
