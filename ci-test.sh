#!/bin/sh -ex

pt () {
    python setup.py test --addopts "$*"
}

if [ "$BACKEND_TEST" ] ; then
    if [ "$SQLITE_TEST" ] ; then
        pt --verbose -m sqlite_source
    fi

    if [ "$POSTGRES_TEST" ] ; then
        psql -c 'DROP DATABASE IF EXISTS test;' -U postgres
        psql -c 'create database test;' -U postgres
        export POSTGRES_URI='postgresql+psycopg2://postgres@localhost/test'
        pt --verbose -m postgres_source
        export POSTGRES_URI='postgresql+pg8000://postgres@localhost/test'
        pt --verbose -m postgres_source
    fi

    if [ "$MYSQL_TEST" ] ; then
        mysql -u root -e 'DROP DATABASE IF EXISTS test;'
        mysql -u root -e 'CREATE DATABASE test DEFAULT CHARACTER SET utf8;'
        mysql -u root -e "CREATE USER IF NOT EXISTS 'test' IDENTIFIED BY 'password';"
        mysql -u root -e "GRANT ALL ON test.* TO 'test';"
        export MYSQL_URI='mysql+mysqlconnector://test:password@localhost/test?charset=utf8&auth_plugin=mysql_native_password'
        pt --verbose -m mysql_source
        export MYSQL_URI='mysql+mysqldb://test:password@localhost/test?charset=utf8'
        pt --verbose -m mysql_source
    fi
else
    pt --verbose -m "'not inttest and not owm_cli_test'" --cov=owmeta
    mv .coverage .coverage-unit
    pt --verbose -m inttest --cov=owmeta
    mv .coverage .coverage-integration
    if [ $WORKERS ] ; then
        pt --workers $WORKERS -m owm_cli_test --cov=owmeta
    else
        pt --verbose -m owm_cli_test --cov=owmeta
    fi
    coverage combine .coverage-integration .coverage-unit .coverage
fi
