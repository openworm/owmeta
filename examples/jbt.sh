#!/bin/sh -ex
# Just Bundle Things
#
# This script runs through some things you can do with owmeta bundles
#
# [BASICS] Creating and listing bundles
# [FETCH] Getting bundles
# [LOCAL] Local index and local cache
# [REMOTE] Remote repositories and distributed file shares
# [INSTALL] Installing a bundle to the local index

# We'll do everything in a temporary directory and clean up at the end
working_directory=$(mktemp -d)
cd $working_directory
cleanup () {
    cd /
    if [ -d "$working_directory" ] ; then
        rm -rf $working_directory
    fi
}

# Clean up when the script exits normally or with an "INT" signal
trap cleanup EXIT INT

# [BASICS]
basic() {
    # To create a bundle, you have to register a bundle descriptor. This is a file which
    # describes what's in a bundle.
    #
    # You can make a bundle descriptor file with any editor you like. It's in YAML
    cat > bundle.yml << HERE
---
id: example/abundle
description: |-
    This is a bundle used for demonstration purposes
includes:
    - http://openworm.org/schema/sci
patterns:
    - rgx:.*data_sources.*#Neurons/context_for.*
    - '*/translators/*'
files:
    includes:
        - src/readme.txt
    patterns:
        - 'src/data_set_0[0-9][0-9]/**'
HERE

    # The `owm bundle register` command actually registers the bundle. This puts a reference
    # to the descriptor file in the .owm directory
    owm bundle register bundle.yml

    # `owm bundle list` lists the bundles registered in this owmeta project
    owm bundle list
    # Output:
    # http://example.org/yep#abundle - This is a bundle used for demonstration purposes

    # If you move or rename a bundle file owmeta will not know about it: it does not track
    # file moves. It will, however, tell you if a bundle descriptor cannot be found when you
    # list registered bundles.
    mv bundle.yml aBundle.yml

    #
    owm bundle list
    # Output:
    # http://example.org/yep#abundle - ERROR: Cannot read bundle descriptor at 'bundle.yml'

    # To correct this, you must re-register the bundle at the new location
    owm register aBundle.yml

    # If you're done with a bundle, you deregister it. You can provide either the descriptor
    # file name or the bundle name
    owm bundle deregister 'example/abundle'

    owm bundle list
    # Output:
    #
}

# [FETCH]
fetch() {
    # [BASIC] showed us how to create and list bundles, but what about when you want
    # someone else's bundles? To fetch a bundle, you need the bundle name. That name is
    # queried for in your local repository (see below in [LOCAL]), then in any remotes
    # configured in your ".owm" directory or user settings, and finally the default remote
    # (see [REMOTE]). `owm bundle fetch` does this for you.
    owm bundle fetch example/bundle.00

    # Fetching a bundle puts it in your local repository so you can use it in any projects on
    # the local machine. You use a bundle in Python with the Bundle object. You can access
    # contexts within a bundle by passing the context to the bundle as shown below.
    use_a_bundle 'example/bundle.01' \
        'https://openworm.org/data#example_bundle_context'

    # Note that the bundle does not need to have been already fetched. use_a_bundle.py, we use
    # a bundle example/bundle.01 which we had not previously
    # fetched. When you make the Bundle object, owmeta will retrieve the bundle from remotes
    # if necessary.
}

# [LOCAL]
local() {
    # The local index keeps track of all of the bundles currently cached on the system from
    # remotes and installed locally. The owmeta.bundle.Bundle class uses the local index to
    # find bundles. The local cache is a directory tree containing bundle contents (i.e.,
    # contexts and associated files).
    #
    # The index is kept up-to-date by various `owm` commands and it is not intended that it be
    # modified by other tools or manually. The index should also not be deleted carelessly --
    # this would render the local cache mostly useless.
    #
    # The files in the local cache are either fetched from remotes or come from bundles
    # installed locally. Bundles may be installed and listed in the index without their files
    # being in the local cache -- this is to allow for keeping data files in an existing
    # directory structure on the local machine. Like with the index, cached files should only
    # be handled through the `owm` commands.
    #
    # To query for bundles in the local index use the `owm bundle index query` command.
    owm bundle index query
    # Output:
    # example/bundle.00 - An example bundle
    # example/bundle.01 - Another example bundle

    # To remove a bundle from the index:
    owm bundle index remove example/bundle.00

    # This will not remove from the cache, however. To remove un-indexed files in the cache,
    # use `owm bundle cache gc`
    owm bundle cache gc
}
# [REMOTE]
# Remotes are places where bundles come from when they aren't in the local cache and where
# bundles go to be shared. The default remote is a maintained by OpenWorm.
#
# TODO: Define a default remote.
# TODO: Define commands for working with remotes
remote () {
}

# [INSTALL]
install() {
    # As stated in [LOCAL], bundles can be installed to the local index. We can install a
    # bundle in our project like this:
    cat > bundle.yml << HERE
---
id: example/abundle
description: |-
    This is a bundle used for demonstration purposes
includes:
    - http://openworm.org/schema/sci
patterns:
    - rgx:.*data_sources.*#Neurons/context_for.*
    - '*/translators/*'
files:
    includes:
        - src/readme.txt
    patterns:
        - 'src/data_set_0[0-9][0-9]/**'
HERE
    owm bundle register bundle.yml
    owm bundle install 'example/abundle'
    # Now we can try
    use_a_bundle 'example/abundle' 'http://openworm.org/schema/sci'
}

use_a_bundle() {
    BUNDLE="$1"
    CONTEXT="$2"
    cat > use_a_bundle.py << HERE
'''
List DataObject sub-classes in the bundle

This is a way to learn a little about the classes in a bundle
'''
from owmeta.bundle import Bundle
from owmeta.context import Context
from owmeta.dataObject import (TypeDataObject,
                               DataObject,
                               RDFSSubClassOfProperty)

# Use the bundle
with Bundle('${BUNDLE}') as bnd:
    # "contextualize" the Context with the bundle to access contexts within the bundle
    ctx = bnd(Context)('${CONTEXT}')

    # Make a query subclasses of BaseDataObject -- the owmeta type which represents RDF
    # resources
    tdo = ctx.stored(TypeDataObject).query()
    tdo.attach_property(RDFSSubClassOfProperty)
    tdo.rdfs_subclassof_property(BaseDataObject.rdf_type_object)

    # Execute the query
    for sc in tdo.load():
        print(sc)
HERE

    python use_a_bundle.py
}
