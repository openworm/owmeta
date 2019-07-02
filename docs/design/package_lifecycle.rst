.. _build_lifecycle:

Data Packaging Lifecycle
========================

The package lifecycle encompasses the creation of data, packaging of said data,
and uploading to shared resources. The data packaging lifecycle draws from the
`Maven build lifecycle <mvn_>`_ in the separation of local actions (e.g.,
``compile``, ``package``, ``install`` phases) from remote interactions (the
``deploy`` phase). To explain why we have these distinct phases, we should step
back and look at what needs to happen when we share data. 

.. _mvn: https://maven.apache.org/guides/introduction/introduction-to-the-lifecycle.html#Packaging

In PyOpenWorm, we may be changing remote resources outside of the PyOpenWorm
system. We also want to support local use and staging of data because it is
expected that there is a lengthy period of data collection/generation,
analysis, curation, and editing which precedes the publication of any data set.
Having separate phases allows us to support a wider range of use-cases with
PyOpenWorm in this local "staging" period. 

To make the above more concrete, the prototypical example for us is around
:py:class:`LocalFileDataSource`, which wants to make the files described in the
data source available for download. Typically, the local path to the file isn't
useful outside of the machine. Also, except for files only a few tens of bytes
in size, it isn't feasible to store the file contents in the same database as
the metadata. We, still want to support metadata about these files and to avoid
the necessity of making *n* different :py:class:`DataSource` sub-classes for
*n* different ways of getting a file. What we do is define a `deploy phase`
that takes every :py:class:`LocalFileDataSource` and "deploys" the files by
uploading them to one or more remote stores or, in the case of a peer-to-peer
solution, by publishing information about the file to a tracker or distributed
hash table.

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
contents of a PyOpenWorm triple store, creates one or more packages from that,
stages the packages for ongoing development, and, finally, deploys packages to
shared resources so that colleagues and other interested parties can access
them. Each phase is associated with a sub-command in :ref:`pow <command>`.

Package
^^^^^^^

*Preparation for distribution.*

When we're generating data, our workspace is not necessarily in the right state
for distribution. We may have created temporary files and notes to ourselves,
or we may have generated data in trial runs or in error that isn't reflective
of our intended experimental conditions. In the packaging phase, we identify
and bring together all and only the data which we wish to distribute for a
given bundle. Furthermore, for us, a package is not meant to change from the
time it is created -- in other words, it is immutable. Consequently, the
packaging phase is an appropriate time for creating summary statistics,
signatures, and content-based identifiers.

One point to note is that the packaging phase does not require that we are
making an archive file of the data. Much of the data which is created in a
research lab is append-only: observations are logged and timestamped either by
a human or by a machine in the moment they happen, but, if done properly, such
logs are rarely edited, or, if there is an amendment, it also is logged as
such, with the original record preserved. As long as this append-only property
is preserved, we only need to designate the range of time-stamped log entries
which belong in a package to obtain an immutable package. Of course, if the
source data is expected to be changed, then we would want either a
copy-on-write mechanism (at the file system level) or a file archive.

The "package", is inert at this point. It can be inspected, and PyOpenWorm will
give information about it, but it is not accessible to PyOpenWorm at run-time
until it is installed.

Install
^^^^^^^

*Local installation. Staging for deployment.* 

The `install` phase takes the package, and adds additional glue to make it
available on the local machine as it would be for a remote machine after
deployment. PyOpenWorm will create a local repository to house installed
packages. The repository stores the relationship between the human-friendly
name for the package (serving a purpose similar to Maven's
group-artifact-version coordinates) and the set of serialized RDF graphs in the
package. Given that the repository is meant to serve a user across projects,
the repository will be stored in the "user directory", if one can be found on
the system. [#userdir]_

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

Deploy
^^^^^^

*Creation of configuration for upload/download. Sharing packages.*

In the "deploy" phase, we publish our packages to "remotes". A "remote" may be
a repository or, in the case of a peer-to-peer file sharing system, a file
index or DHT.

In the "deploy" phase, we can add additional information about how and where
things are deployed. 

.. [#userdir]  This will be the user directory as determined by
   :py:func:`os.path.expanduser`

