#!/bin/sh -ex

pip install -e .
pip install coveralls
pip install -r test-requirements.txt
owm clone https://github.com/openworm/OpenWormData.git --branch owmeta
if [ $BUNDLE_TESTS ] ; then
    owm bundle register ./owmeta-schema-bundle.yml
    owm bundle register ./owmeta-data-bundle.yml
    owm bundle install openworm/owmeta-schema
    owm bundle install openworm/owmeta-data
fi
if [ "$PYTHON_VERSION" == "3.6" ] ; then
    # pyparsing 3.0 no longer allows setting the .name attribute for
    # TokenConverter, but the fix for that only goes in RDFLib 6 which
    # does not support Python 3.6. See
    # https://github.com/RDFLib/rdflib/issues/1190 and
    # https://github.com/rdflib/rdflib/issues/1370 for details on the issue.
    #
    # Since we're a library, it's up to the user how to resolve this
    # (e.g., ignore and do not use SPARQL) so we do not impose any
    # version constraints in package metadata, just adjust so the build
    # passes
    pip install 'pyparsing<3.0.0'
fi
