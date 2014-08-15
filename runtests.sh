#!/bin/bash
if [ $1 ] ; then 
    if [ "$1" = itest ] ; then 
        if [ "$2" ] ; then 
            python -m unittest tests.integration_test.IntegrationTest.$2
        else
            python -m unittest tests.integration_test.IntegrationTest
        fi
    else
        python -m unittest tests.test.$1
    fi
else
    for x in tests/test_*.conf ; do
        cp $x tests/_test.conf
        echo Testing with $x
        python -m unittest tests.test 2> ${x/.conf}.log
        tail -n 3 ${x/.conf}.log
        echo -----------------------------------------------------------------
    done
    #python -m unittest tests.integration_test
fi

