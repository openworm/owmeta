from __future__ import absolute_import
from rdflib import Graph
from FuXi.Rete.RuleStore import SetupRuleStore

from FuXi.Rete.Util import generateTokenSet
from FuXi.Horn.HornRules import HornFromN3

rule_store, rule_graph, network = SetupRuleStore(makeNetwork=True)

closureDeltaGraph = Graph()

network.inferredFacts = closureDeltaGraph

for rule in HornFromN3('rules.n3'): 
    network.buildNetworkFromClause(rule)

factGraph = Graph().parse('facts.n3',format='n3')

network.feedFactsToAdd(generateTokenSet(factGraph))

inferred_facts = closureDeltaGraph.serialize(format='n3')

#write inferred facts to file
inferred = open('inferred.n3', 'w')
inferred.write(inferred_facts)
inferred.close()