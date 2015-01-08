C. elegans database
--------------------

This repository contains a database stored in N3 format. It is meant to be used with [PyOpenWorm](https://github.com/openworm/PyOpenWorm/tree/alpha0.5).

Compiled from the content at:

1. [Tim Busbice's interactive database](http://www.interintelligence.org/openworm/), stored as a sqlite database in this repository
2. [C. elegans Cell lists](https://docs.google.com/spreadsheet/ccc?key=0Avt3mQaA-HaMdGFnQldkWm9oUmQ3YjZ1LXJ4OHFnR0E&usp=drive_web#gid=1), stored as tsv files in this repository

See 'scripts/serialize_it.py' for writing your binary database (e.g. 'worm.db') to a file like 'out.n3' for sharing.
