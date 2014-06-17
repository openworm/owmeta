if [ $1 ] ; then 
    python -m unittest tests.test.$1
else
    python -m unittest discover -s tests
fi

