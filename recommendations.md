###add_reference.py

Printing Evidence object gives duplicates of `doi` and `pmid`.
May be related to [comment in evidence.py](https://github.com/openworm/PyOpenWorm/blob/alpha0.5/PyOpenWorm/evidence.py#L139)

###apsp.py

This is used in `shortest_path.py`.
There is no dependency on `numpy` enforced, so had to install it manually.

###aval.xml

Seems this is needed for `morpho.py`.

###default.conf

Configuration for connecting to database.
Used in `NetworkInfo.py`.

###gap_junctions.py

Used to connect to db with `testconf=true`, but this option doesn't exist anymore.
There was nothing to do with gap junctions here, so I made an example on how to get gap junctions from the database.

###morph.conf

This doesn't seem to be used anywhere. Safe to delete it.

###morpho.py

Adjusted to work with dummy db configuration.

###NeuronBasicInfo.py

Adjusted so now it gives the correct output (names of neurons in each neuron type category).
Something is wrong though, and may just be my version of the db or something, but it only prints out one neuron and its type.
I checked some neurons manually, and they practically all had nothing under their `type` attribute.

###NetworkInfo.py

Adjusted the script so it works with this version of PyOW, and the printing to be slightly more meaningful to a reader.
Note that the output is off because if prints "E" for all neurons connected by "send" (i.e. a synapse).
I did manual queries of some of the neurons (`myNeuron.type.one()`) and found that practically none of them had anything registered for this value (i.e. a neurotransmitter).
Again, this may be my version of the db, but I believe it is up-to-date.

###rmgr.py

I couldn't figure out what this script is doing, but it executes successfully.
Best to contact the original author on this one.

###shortest_path.py

This was already well-commented so I didn't have to add much.

###test_bgp.py

This is pretty straightforward and just loads things from the database.
