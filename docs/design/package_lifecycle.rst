.. _package_lifecycle:

Data Packaging Lifecycle
========================

The package lifecycle encompasses the creation of data, packaging of said data,
and uploading to shared resources. The data packaging lifecycle draws from the
`Maven build lifecycle <mvn_>`_ in the separation of local actions (e.g.,
``compile``, ``stage``, ``install`` phases) from remote interactions (the
``deploy`` phase). To explain why we have these distinct phases, we should step
back and look at what needs to happen when we share data. 

.. _mvn: https://maven.apache.org/guides/introduction/introduction-to-the-lifecycle.html#Packaging

In |pow|, we may be changing remote resources outside of the |pow| system. We
also want to support local use and staging of data because it is expected that
there is a lengthy period of data collection/generation, analysis, curation,
and editing which precedes the publication of any data set.  Having separate
phases allows us to support a wider range of use-cases with |pow| in this local
"staging" period. 

To make the above more concrete, the prototypical example for us is around
:py:class:`~PyOpenWorm.data_trans.local_file_ds.LocalFileDataSource`, which
wants to make the files described in the data source available for download.
Typically, the local path to the file isn't useful outside of the machine.
Also, except for files only a few tens of bytes in size, it isn't feasible to
store the file contents in the same database as the metadata. We, still want to
support metadata about these files and to avoid the necessity of making *n*
different :py:class:`~PyOpenWorm.datasource.DataSource` sub-classes for *n*
different ways of getting a file. What we do is define a "deploy" phase that
takes every
:py:class:`~PyOpenWorm.data_trans.local_file_ds.LocalFileDataSource` and
"deploys" the files by uploading them to one or more remote stores or, in the
case of a peer-to-peer solution, by publishing information about the file to a
tracker or distributed hash table.

Packaging proceeds in phases to serve as an organizational structure for data
producers, software developers, management, and information technology
personnel. Compared with a more free-form build strategy like using an amalgam
of shell scripts and disconnected commands, or even rule-based execution (e.g.,
`GNU make <make_>`_), phases organize the otherwise implicit process by which the
local database gets made available to other people. This explicitness is very
useful since, when different people can take different roles in creating the
configuration for each phase, having named phases where things happen aids in
discussion, process development, and review.  For instance, junior lab
technicians may be responsible for creating or maintaining packaging with
guidance from senior technicians or principal investigators. IT personnel may
be interested in all phases since they all deal with the computing resources
they manage, but they may focus on the phases that affect "remote" resources
since those resources may, in fact, be managed within the same organization and
require more effort in sharing URLs, generating access credentials, etc. 

.. _make: https://www.gnu.org/software/make/manual/html_node/index.html

The remainder of this document will describe the default lifecycle and what
takes place within each phase. 

Default Lifecycle
-----------------

The default lifecycle takes a :ref:`bundle <project_bundles>`, including the
contents of a |pow| triple store, creates one or more packages from that,
stages the packages for ongoing development, and, finally, deploys packages to
shared resources so that colleagues and other interested parties can access
them. Each phase is associated with a sub-command in :ref:`pow <command>`.

.. _package_lifecycle_stage_phase:

Stage
^^^^^

*Preparation for distribution.*

When we're generating data, our workspace is not necessarily in the right state
for distribution. We may have created temporary files and notes to ourselves,
or we may have generated data in trial runs (or by mistake) which do not
reflect our formal experimental conditions. In the staging phase, we bring
together just the data which we wish to distribute for a given bundle.  |RDF|
data During the staging phase we also serialize 

Once
these data are brought together in the staging area, they should be immutable
-- in other words, they should not change any more. Consequently, the packaging
phase is the appropriate time for creating summary statistics, signatures, and
content-based identifiers.


For files associated with staged |RDF| data, Much of the data which is created
in a research lab is append-only: observations are logged and timestamped
either by a human or by a machine in the moment they happen, but, if done
properly, such logs are rarely edited, or, if there is an amendment, it also is
logged as such, with the original record preserved. As long as this append-only
property is preserved, we only need to designate the range of such time-stamped
records which belong in a package to have the desired immutability. Of course,
if the source data is expected to be changed, then we would want either a
copy-on-write mechanism (at the file system level) or to copy the files.
Regardless, file hashes and/or signatures created during the staging phase
would be available for guarding against accidental changes.

Install
^^^^^^^

*Local installation. Preparation for deployment.* 

The "install" phase takes the staged data, and adds additional glue to make it
available on the local machine as it would be for a remote machine after
deployment. |pow| will create a local repository to house installed
packages. The repository stores the relationship between the human-friendly
name for the package (serving a purpose similar to Maven's
group-artifact-version coordinates) and the set of serialized |RDF| graphs in
the package. Given that the repository is meant to serve a user across
projects, the repository will be stored in the "user directory", if one can be
found on the system. [#userdir]_

Continuing the pattern of putting configuration in RDF form, the repository is
also described as in RDF and shall use the same form as remote repositories, up
to a substitution of access protocols (e.g., file system access in place of
HTTP access). The value here is in interoperability and ease of implementation.
For the first point, we have fairly broad support for RDF query and
manipulation across programming languages. The second point is supported by the
first and by the fact that, once we've got implementations for the necessary
access methods, no additional code should need to be written for access to
remote repositories beyond what's done for local.

The same argument about immutability of data files applies to the install phase
as well. Installed packages may still have references to paths on the local
file system. It is not until the deploy phase that all local paths must be
expunged.

.. _package_lifecycle_deploy_phase:

Deploy
^^^^^^

*Creation of configuration for upload/download. Sharing packages.*

In the "deploy" phase, we publish our data to "remotes". A "remote" may be a
repository or, in the case of a peer-to-peer file sharing system, a file index
or DHT. Above, we referred to non-RDF data files on the local file system --
during the deploy phase, these files are actually published and accession
information (e.g., a database record identifier) for those files is generated
and returned to the system where the deployment was initiated. This assumes a
fully automated process for publication of files: If, instead, the publication
platform requires some manual interaction, that must be done outside of |pow|
and then the accession information would be provided with the deploy command.

.. [#userdir]  This will be the user directory as determined by
   :py:func:`os.path.expanduser`

