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
        rm $COVERAGES
    fi
}

trap cleanup_coverage EXIT

if [ "$SQLITE_TEST" ] ; then
    pt --verbose -m sqlite_source
    add_coverage
fi

if [ "$POSTGRES_TEST" ] ; then
    psql -c 'DROP DATABASE IF EXISTS test;' -U postgres
    psql -c 'create database test;' -U postgres
    export POSTGRES_URI='postgresql+psycopg2://postgres@localhost/test'
    pt --verbose -m postgres_source
    add_coverage
    export POSTGRES_URI='postgresql+pg8000://postgres@localhost/test'
    pt --verbose -m postgres_source
    add_coverage
fi

if [ "$MYSQL_TEST" ] ; then
    mysql -u root -e 'DROP DATABASE IF EXISTS test;'
    mysql -u root -e 'CREATE DATABASE test DEFAULT CHARACTER SET utf8;'
    mysql -u root -e "CREATE USER IF NOT EXISTS 'test' IDENTIFIED BY 'password';"
    mysql -u root -e "GRANT ALL ON test.* TO 'test';"
    export MYSQL_URI='mysql+mysqlconnector://test:password@localhost/test?charset=utf8&auth_plugin=mysql_native_password'
    pt --verbose -m mysql_source
    add_coverage
    export MYSQL_URI='mysql+mysqldb://test:password@localhost/test?charset=utf8'
    pt --verbose -m mysql_source
    add_coverage
fi
pt --verbose -m "'not inttest and not owm_cli_test'"
add_coverage
pt --verbose -m inttest
add_coverage
if [ $WORKERS ] ; then
    pt --workers $WORKERS -m owm_cli_test
else
    pt --verbose -m owm_cli_test
fi
add_coverage
coverage combine $(list_coverage)
