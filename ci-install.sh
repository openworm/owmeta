#!/bin/sh -ex

TARGET=.
if [ "$MYSQL_SOURCE" ] ; then
    TARGET=".[mysql_source_mysql_connector] .[mysql_source_mysqlclient]"
fi

if [ "$POSTGRES_SOURCE" ] ; then
    TARGET=".[postgres_source_psycopg] .[postgres_source_pg8000]"
fi

pip install $TARGET
