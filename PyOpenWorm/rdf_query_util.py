import rdflib


def goq_hop_scorer(hop):
    if hop[1] == rdflib.RDF.type:
        return 1
    return 0
