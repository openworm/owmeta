#!/bin/sh -ex

pt () {
    sh -c "pytest --cov=owmeta $*"
}


COVERAGES=""

add_coverage () {
    tempname="$(mktemp ow-meta-test-coverage.XXXXXXXXXX)"
    cat .coverage > $tempname
    COVERAGES="$COVERAGES $tempname"
}

list_coverage () {
    echo $COVERAGES
}

cleanup_coverage () {
    if [ "$COVERAGES" ] ; then
        rm -f $COVERAGES
    fi
}

trap cleanup_coverage EXIT

if [ $DATA_BUNDLE_TESTS ] ; then
    pt --verbose -m data_bundle
    add_coverage
else
    pt --verbose -m "'not inttest'"
    add_coverage
    pt --verbose -m "'inttest and not data_bundle'"
    add_coverage
fi
coverage combine $(list_coverage)
