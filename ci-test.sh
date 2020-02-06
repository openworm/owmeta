#!/bin/sh -ex

pt () {
    python setup.py test --addopts "$* --cov=owmeta"
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

pt --verbose -m "'not inttest'"
add_coverage
pt --verbose -m inttest
add_coverage
coverage combine $(list_coverage)
