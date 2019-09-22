#!/bin/sh

BRANCH=${TRAVIS_BRANCH:-$(git symbolic-ref --short HEAD)}
ENV=travis-ci
COMMIT=$(git rev-parse HEAD)
OWCS_USERNAME=travisci
echo "Branch: $BRANCH"
echo "Environment: $ENV"
echo "Commit: $COMMIT"
echo "User: $OWCS_USERNAME"
URL=${OWCS_URL:-https://owcs.pythonanywhere.com/}

py.test $@ --code-speed-submit="$URL" \
    --environment="$ENV" --branch="$BRANCH" --commit="$COMMIT" \
    --project=owmeta --password=${OWCS_KEY} --username=$OWCS_USERNAME \
    ./tests/ProfileTest.py
