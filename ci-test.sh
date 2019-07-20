#!/bin/sh -ex

pt () {
    python setup.py test --addopts "$* --cov=PyOpenWorm"
}
pt --verbose -m "'not inttest and not pow_cli_test'"
mv .coverage .coverage-unit
pt --verbose -m inttest
mv .coverage .coverage-integration
if [ $WORKERS ] ; then
  pt --workers $WORKERS -m pow_cli_test
else
  pt --verbose -m pow_cli_test
fi
coverage combine .coverage-integration .coverage-unit .coverage

