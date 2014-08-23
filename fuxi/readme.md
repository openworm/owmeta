#FuXi integration

FuXi is implemented as a semantic reasoning layer in PyOpenWorm. Its purpose here is to automate the setting of various properties (ex: class-subclass relationships), rather than programming them by hand.

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
`Demo` folder contains `facts.n3` with a single fact, and `rules.n3` which contains a single rule.     
<br>
`test_fuxi.py` is a test script adapted from the FuXi docs that shows the rule being applied, and prints the inferred fact(s) to a new file.  
<br>
`testrules.n3` contains the rule(s) to be applied when insert_worm is run. In this version, each muscle object is given type worm:TestClass.