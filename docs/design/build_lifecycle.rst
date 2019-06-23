.. _build_lifecycle:

Data Packaging Lifecycle
========================

The package lifecycle encompasses the creation of data, packaging of said data,
and uploading to shared resources. The data packaging lifecycle draws from the
`Maven build lifecycle <mvn_>`_ in the separation of local actions (e.g.,
``compile``, ``package``, ``install`` phases) from remote interactions (the
``deploy`` phase). To explain why we have these distinct phases, we should step
back and look at what needs to happen when we share data. 

In PyOpenWorm, we can be changing remote resources outside of the PyOpenWorm
system but which are referred to from within the graph. The prototypical
example is :py:class:`LocalFileDataSource`, which wants to make files available
for download that exist outside of the RDF graph. In the ``deploy`` phase, a
``LocalFileDataSource`` would have its local copies of a file uploaded to a
remote resource.

We don't need to "package" files locally except for purposes of compression
since there's a lot of redundancy in our data format and there's a lot of
triples in our graph serializations.

In the "deploy" phase, we can modify the graph to have additional info about
how and where things are deployed. In software, we would generally need to
unzip and repackage if we needed to make modifications to the contents of a
package. For our graph data, we don't have a reason to put our files in an
archive except to free up disk space. We may need to copy from the place where
we staged our files so that we can create additional deployments from
previously staged copies, but we wouldn't need to make an actual archive file.

One difficulty I should point to though is that of "signing" and "hashing". If
we're introducing another layer in the form of file access metadata, then we
would need to introduce a step for hashing  The deploy phase is basically the packaging
I
want to allow users to 
need


.. _mvn: https://maven.apache.org/guides/introduction/introduction-to-the-lifecycle.html#Packaging
