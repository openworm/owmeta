#!/bin/sh -ex

pt () {
    python setup.py test --addopts "$* --cov=owmeta"
}

if [ "$SQLITE_SOURCE" ] ; then
    pt --verbose -m sqlite_source
fi

if [ "$POSTGRES_SOURCE" ] ; then
    psql -c 'DROP DATABASE IF EXISTS test;' -U postgres
    psql -c 'create database test;' -U postgres
    export POSTGRES_URI='postgresql+psycopg2://postgres@localhost/test'
    pt --verbose -m postgres_source
    export POSTGRES_URI='postgresql+pg8000://postgres@localhost/test'
    pt --verbose -m postgres_source
fi

if [ "$MYSQL_SOURCE" ] ; then
    mysql -e 'CREATE SCHEMA test DEFAULT CHARACTER SET utf8;'
    export MYSQL_URI='mysql+mysqlconnector://test@localhost/test?charset=utf8'
    pt --verbose -m mysql_source
    export MYSQL_URI='mysql+mysqlclient://test@localhost/test?charset=utf8'
    pt --verbose -m mysql_source
fi

pt --verbose -m "'not inttest and not owm_cli_test'"
mv .coverage .coverage-unit
pt --verbose -m inttest
mv .coverage .coverage-integration
if [ $WORKERS ] ; then
  pt --workers $WORKERS -m owm_cli_test
else
  pt --verbose -m owm_cli_test
fi
coverage combine .coverage-integration .coverage-unit .coverage

