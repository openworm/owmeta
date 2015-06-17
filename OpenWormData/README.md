C. elegans database
--------------------

This repository contains a database stored in N3 format. It is meant to be used with [PyOpenWorm](https://github.com/openworm/PyOpenWorm/tree/alpha0.5).

Compiled from the content at:

1. [Tim Busbice's interactive database](http://www.interintelligence.org/openworm/), stored as a sqlite database in this repository
2. [C. elegans Cell lists](https://docs.google.com/spreadsheet/ccc?key=0Avt3mQaA-HaMdGFnQldkWm9oUmQ3YjZ1LXJ4OHFnR0E&usp=drive_web#gid=1), stored as tsv files in this repository.
3. [Neuronal network details spreadsheet](https://docs.google.com/spreadsheets/d/1Jc9pOJAce8DdcgkTgkUXafhsBQdrer2Y47zrHsxlqWg/edit#gid=2), used for data about neurons. Stored in the `aux_data/neurons.csv` file.

See 'scripts/insert_worm.py' to regenerate the binary database from original sources.

See 'scripts/serialize_it.py' for writing your binary database (e.g. 'worm.db') to a file like 'out.n3' for sharing.

N3 Syntax (directly from Wikipedia)
-----------------------------------

(quoting [from here](https://en.wikipedia.org/wiki/Notation3))

Notation3, or N3 as it is more commonly known, is a shorthand non-XML serialization of Resource Description Framework
models, designed with human-readability in mind: N3 is much more compact and readable than XML RDF notation. The format
is being developed by Tim Berners-Lee and others from the Semantic Web community. A formalization of the logic underlying
N3 was published by Berners-Lee and others in 2008.

N3 has several features that go beyond a serialization for RDF models, such as support for RDF-based rules. Turtle is a
simplified, RDF-only subset of N3.

Examples
--------

This RDF model in standard XML notation

```
<rdf:RDF
xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
xmlns:dc="http://purl.org/dc/elements/1.1/">
<rdf:Description rdf:about="http://en.wikipedia.org/wiki/Tony_Benn">
<dc:title>Tony Benn</dc:title>
<dc:publisher>Wikipedia</dc:publisher>
</rdf:Description>
</rdf:RDF>
```

may be written in Notation 3 like this:

```
@PREFIX dc: <http://purl.org/dc/elements/1.1/>.

<http://en.wikipedia.org/wiki/Tony_Benn>
dc:title "Tony Benn";
dc:publisher "Wikipedia".
```
