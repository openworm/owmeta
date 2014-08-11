from rdflib import Graph
from FuXi.Rete.RuleStore import SetupRuleStore

from FuXi.Rete.Util import generateTokenSet
from FuXi.Horn.HornRules import HornFromN3

rule_store, rule_graph, network = SetupRuleStore(makeNetwork=True)
closureDeltaGraph=Graph()
network.inferredFacts = closureDeltaGraph
for rule in HornFromN3('demo/rules.n3'): network.buildNetworkFromClause(rule)
factGraph = Graph().parse('demo/facts.n3',format='n3')
network.feedFactsToAdd(generateTokenSet(factGraph))
print closureDeltaGraph.serialize(format='n3')