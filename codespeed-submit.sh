#!/bin/sh

py.test $@ --cov=PyOpenWorm --code-speed-submit="https://owcs.pythonanywhere.com/" \
    --environment="travis-ci" --branch="$(git symbolic-ref --short HEAD)" \
    --commit="$(git rev-parse HEAD)" --password=${OWCS_KEY} --username=travisci ./tests/ProfileTest.py
