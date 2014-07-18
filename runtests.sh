if [ $1 ] ; then 
    if [ "$1" = itest ] ; then 
        python -m unittest tests.integration_test.IntegrationTest.$2
    else
        python -m unittest tests.test.$1
    fi
else
    python -m unittest discover -s tests
fi

