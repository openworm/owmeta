.. _data_requirements:

Requirements for data storage in OpenWorm
=========================================
Our OpenWorm database captures facts about C. `elegans`. The database stores data for generating model files and together with annotations describing the origins of the data. Below are a set of recommendations for implementation of the database organized around an RDF model. 

Why RDF?
---------
RDF offers advantages in resilience to schema additions and increased flexibility in integrating data from disparate sources. [1]_ These qualities can be valued by comparison to relational database systems. Typically, schema changes in a relational database require extensive work for applications using it. [2]_ In the author's experience, RDF databases offer more freedom in restructuring. Also, for data integration, SPARQL, the standard language for querying over RDF has `Federated queries <http://www.w3.org/TR/sparql11-federated-query/>`_ which allow for nearly painless integration of external SPARQL endpoints with existing queries.

.. [1] http://answers.semanticweb.com/questions/19183/advantages-of-rdf-over-relational-databases
.. [2] http://research.microsoft.com/pubs/118211/andy%20maule%20-%20thesis.pdf


Interface
---------
Access is through a Python library which communicates with the database. This library serves the function of providing an object oriented view on the database that can be accessed through the Python scripts commonly used in the project. The :ref:`draft api <api>` is described separately.

Data modelling
--------------
Biophysical and anatomical data are included in the database. A sketch of some proposed features of the data model is below. Also included in our model are the relationships between these types. Given our choice of data types, we do not model the individual interactions between cells as entities in the database. Rather these are described by generic predicates in an `RDF triple <http://stackoverflow.com/a/1122451>`__. For instance, neuron A synapsing with muscle cell B would give a statement (A, synapsesWith, B), but A synapsing with neuron C would also have (A, synapsesWith, C). Data which belong to the specific relationship between two nodes is attached to an `rdf:Statement object <http://www.w3.org/TR/rdf-schema/#ch_statement>`__ which points to the statement. This choice is intended to easy querying and extension later on.

Nervous system
~~~~~~~~~~~~~~
In the worm's nervous system, we capture a few important data types (listed `below <#datatypes>`__). These correspond primarily to the anatomical structures and chemicals which are necessary for the worm to record external and internal stimuli and activate its body in response to those stimuli.

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
Caenorhabditis elegans has very stable cell division patterns in the absence of mutations. This means that we can capture divisions in our database as static 'daughter_of' relationships. The theory of differentiation codes additionally gives an algorithmic description to the growth patterns of the worm which describes signals transmitted between developing cells. TIn order to test this theory we would like to leverage existing photographic data indicating the volume of cells at the time of their division as this relates to the differentiation code stored by the cell. Progress on this issue is documented `on Github <https://github.com/openworm/PyOpenWorm/issues/7#issuecomment-45401916>`_.

Aging
~~~~~
Concurrently with development, we would like to begin modeling the effects of aging on the worm. Aging typically manifests in physiological changes due to transcription errors or cell death. These physiological changes can be represented abstractly as parameters to the function of biological entities. See `Github <https://github.com/openworm/PyOpenWorm/issues/6>`_ for further discussion.

Information assurance
---------------------

Reasoning and Data integrity
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
To make full use of RDF storage it's recommended to leverage reasoning over our stored data. Encoding rules for the worm requires a good knowledge of both C. elegans and the database schema. More research needs to be done on this going forward. Preliminarily, SPIN, a constraint notation system based on SPARQL looks like a good candidate for `specifying` rules, but an inference engine for `enforcing` the rules still needs to be found.

Input validation
~~~~~~~~~~~~~~~~
Input validation is to be handled through the interface library referenced `above <#interface>`_. In general, incorrect entry of biological names will result in an error being reported identifying the offending entry and providing a acceptable entries where appropriate. No direct access to the underlying data store will be provided.

Provenance
~~~~~~~~~~
As stated in the opening paragraph, tracking the origins of facts stated in the database demands a method of annotating statements in our database. Providing citations for facts must be as simple as providing a global identifier (e.g., URI, DOI) or a local identifier (e.g., Bibtex identifier, Pubmed ID). A technique called RDF reification allows us to annotate arbitrary facts in our database with additional information. This technique allows for the addition of structured citation data to facts in the database as well as annotations for tracking responsibility for uploads to the database. Further details for the attachment of evidence using this technique are given in the :ref:`draft api <api>`.

In line with current practices for communication through the source code management platform, Github, we would like to track responsibility for new uploads to the database. Two methods are proposed for tracking this information: RDF named graphs and RDF reification. Tracking information must include, at least, a time-stamp on the update and linking of the submitted data to the uploader's unique identifier (e.g., email address). Named graphs have the advantage of wide support for the use of tracking uploads. The choice between these depends largely the support of the chosen data store for named graphs.

Access control
~~~~~~~~~~~~~~~~~
Write access to data in the project has been inconsistent between various data sources in the project. Going forward, write access to OpenWorm databases should be restricted to authenticated users to forestall the possibility of malicious tampering. 

Storage options
~~~~~~~~~~~~~~~

Physical storage
+++++++++++++++++++

Candidates:
Considering main memory necessary for joins.

- DigitalOcean (Currently used)
  - Pricing: $.03 per hour of usage - capped at 5/month.
  - Storage capacity: 20GB
  - Data transfer: 1TB
  - Main memory: 1 GB
  - Other plans here: https://www.digitalocean.com/pricing/
- Amazon EC2
  - Pricing: ???
  - Scalable service
- Linode
  - Pricing: $.03 per/hour of usage - capped at $20/month.

Availability
++++++++++++++
A concern for OpenWorm as a project designed for wide dissemination of knowledge to the scientific community and to the public presents a challenge for us in keeping source data available for presentation. As yet, the demands on proposed database servers have not been determined. Cloud storage options must be further explored. As the projected size of the database is merely several gigabytes, migration is not a major concern at this point.

Store software
++++++++++++++++++

For the time being, OpenRDF Sesame's memory store will serve as the storage for the project. Other store softwares are being evaluated.

Testing:

- OpenRDF Sesame
    - Free, open source
    - `REST interface <http://openrdf.callimachus.net/sesame/2.7/docs/system.docbook?view#The_Sesame_REST_HTTP_Protocol>`_
    - `Java interface (SAIL API) <http://openrdf.callimachus.net/sesame/2.7/docs/users.docbook?view#The_Repository_API>`_
    - RDFS reasoning
- Ontotext OWLIM
    - Free "lite" version, proprietary
    - Uses Openrdf Sesame interface 
    - OWL & RDFS reasoning

Not Yet Evaluated:

- Apache Jena TDB
    - Free, open source
    - Java interface
- Apache Jena Fuseki
    - Free, open source
    - REST interface
- 3store
- 4store
- Allegro Graph
- Openlink Virtuoso

Miscellaneous 
-------------
Versioning
~~~~~~~~~~
Experimental methods are constantly improving in biological research. These improvements may require updating the data we reference or store internally. However, in making updates we must not immediately expunge older content, breaking links created by internal and external agents. Ideally we would have a means of deprecating old data and specifying replacements. On the level of single resources, this is a trivial mapping which may be done transparently to all readers. For a more significant change, altering the schema, human intervention may be required to update external readers.
