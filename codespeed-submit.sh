#!/bin/sh

BRANCH=${TRAVIS_BRANCH:-$(git symbolic-ref --short HEAD)}

py.test $@ --cov=PyOpenWorm --code-speed-submit="https://owcs.pythonanywhere.com/" \
    --environment="travis-ci" --branch="$BRANCH" \
    --commit="$(git rev-parse HEAD)" --password=${OWCS_KEY} --username=travisci ./tests/ProfileTest.py
