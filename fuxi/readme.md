#FuXi integration

FuXi is implemented as a semantic reasoning layer in PyOpenWorm. Its purpose here is to reduce the number of triples explicitly stored in the PyOpenWorm database by generating new connections in the graph. This should decrease loading time and reduce the size of the database file.

<br>
## How it works
<br>
FuXi takes a list of **rules** and applies them exhaustively to a set of **facts**, inferring **new facts** as a result. A simple pseudocode example follows:

A rule might be:

* { x is "Neuron" } => { x is "Cell" }

And a fact might be:

* { "ADLR" is "Neuron" }

Given the above rule and fact, FuXi could infer the new fact:

* { "ADLR" is "Cell" }

<br>
##Installing FuXi    
<br>
Navigate to the directory you want to install FuXi in, then do:  
`git clone https://github.com/RDFLib/FuXi.git`  
`cd FuXi`  
`python setup.py install`   
<br>
##Files
<br>
* `Demo` folder contains `facts.n3` for a single Neuron object, and `rules.n3` which implements the p[seudocode described above.   
* `test_fuxi.py` is a test script adapted from the FuXi docs that shows the rule being applied, and prints out the inferred fact.
<br>