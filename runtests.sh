#!/bin/bash

cp tests/test_default.conf tests/_test.conf
if [ $1 ] ; then 
    if [ "$1" = itest ] ; then 
        if [ "$2" ] ; then 
            python -m unittest tests.integration_test.IntegrationTest.$2
        else
            python -m unittest tests.integration_test.IntegrationTest
        fi
    elif [ "$1" = conf ] ; then
        if [ -f "$2" ] ; then
            # use nose to run with the given config file
            cp "$2" tests/_test.conf
            python -m unittest tests.test
        fi
    else
        python -m unittest tests.test.$1
    fi
else
    # Run with all detected configuration files in tests/
    test_result=0
    bad_files=
    for x in tests/test_*.conf ; do
        log=${x/.conf}.log
        cp $x tests/_test.conf
        echo Testing with $x
        python -m unittest tests.test 2> $log
        if [ $? -ne 0 ] ; then
            test_result=1
            bad_files="$bad_files $log"
        fi
        tail -n 3 $log
        echo '-------------[END OF TEST]-----------' >> $log
        echo -----------------------------------------------------------------
    done
    echo | cat $bad_files
    exit $test_result
    python -m unittest tests.integration_test
fi

