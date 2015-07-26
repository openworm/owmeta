How To Generate Performance Profiles
====================================

The following example generates a performance profile for the
PyOpenWorm test suite. No modification to any code in PyOpenWorm is
necessary. Currently observed instrumentation overhead is about 30%
but that should not be a big problem for serial code, and there should
be ways to reduce the instrumentation overhead:

python -m cProfile -o PyOpenWormTests.out tests/test.py

The output from the above command creates a binary profile which
includes a lot more information than we'd currently use (and can
include callpath information). We can trim this down by focusing on a
plain performance profile of only PyOpenWorm user functions sorted by
cumulative time spent. This will help us focus on the most expensive
function calls that our code makes, and is a reasonable low-hanging
fruit for performance regression.

python perfOutput.py PyOpenWormTests.out > PyOpenWorm_PerfUser.txt

Output Example
==============

Sun Jul 12 22:00:29 2015    PyOpenWorm_Tests.out

         211211100 function calls (208175764 primitive calls) in 290.995 seconds

   Ordered by: cumulative time, internal time, call count
   List reduced from 4523 to 229 due to restriction <'PyOpenWorm'>

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000   64.107   64.107 ./PyOpenWorm/__init__.py:125(loadData)
       66    0.002    0.000   32.876    0.498 ./PyOpenWorm/evidence.py:229(__init__)
       54    0.001    0.000   32.716    0.606 ./PyOpenWorm/evidence.py:23(_url_request)
       24    0.001    0.000   27.919    1.163 ./PyOpenWorm/evidence.py:297(_wormbase_extract)
       48    0.000    0.000   27.874    0.581 ./PyOpenWorm/evidence.py:302(wbRequest)
       48    0.001    0.000   27.874    0.581 ./PyOpenWorm/evidence.py:34(_json_request)
  519/509    0.001    0.000   23.415    0.046 ./PyOpenWorm/data.py:199(add_statements)
  519/509    0.021    0.000   23.414    0.046 ./PyOpenWorm/data.py:119(_add_to_store)
  886/855    0.004    0.000   20.391    0.024 ./PyOpenWorm/dataObject.py:522(__call__)
     1593    0.022    0.000   13.160    0.008 ./PyOpenWorm/dataObject.py:582(get)
      118    0.000    0.000   10.802    0.092 ./PyOpenWorm/data.py:259(closeDatabase)
      116    0.001    0.000   10.802    0.093 ./PyOpenWorm/data.py:589(close)
      116    0.001    0.000   10.792    0.093 ./PyOpenWorm/__init__.py:110(disconnect)
      469    0.004    0.000   10.326    0.022 ./PyOpenWorm/dataObject.py:621(set)
      363    0.000    0.000    8.246    0.023 ./PyOpenWorm/configure.py:122(get)
        2    0.000    0.000    8.245    4.123 ./PyOpenWorm/network.py:75(as_networkx)
        2    0.000    0.000    8.245    4.123 ./PyOpenWorm/dataObject.py:377(__getitem__)
        2    0.000    0.000    8.245    4.123 ./PyOpenWorm/configure.py:144(__getitem__)
        2    0.000    0.000    8.245    4.123 ./PyOpenWorm/data.py:33(get)
