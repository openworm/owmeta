# -*- coding: utf-8 -*-

import sys
sys.path.insert(0,".")
import unittest
import neuroml
import neuroml.writers as writers
import PyOpenWorm
from PyOpenWorm import *
import networkx
import rdflib
import rdflib as R
import pint as Q
import os
import subprocess as SP
import subprocess
import tempfile
import doctest

from glob import glob

from rdflib import Graph
from FuXi.Rete.RuleStore import SetupRuleStore

from FuXi.Rete.Util import generateTokenSet
from FuXi.Horn.HornRules import HornFromN3

class InferenceTest(unittest.TestCase):
    
    def test_make_inference(self):
        """
        Tests that the rule engine is able to fire and make an inference.
        This passes if any inference at all is generated.
        """

        rule_store, rule_graph, network = SetupRuleStore(makeNetwork=True)

        closureDeltaGraph = Graph()

        network.inferredFacts = closureDeltaGraph

        for rule in HornFromN3('tests/fuxi_test_files/rules.n3'): 
            network.buildNetworkFromClause(rule)

        factGraph = Graph().parse('tests/fuxi_test_files/facts.n3',format='n3')

        network.feedFactsToAdd(generateTokenSet(factGraph))

        inferred_facts = list(closureDeltaGraph.objects())

        assert len(inferred_facts) > 0

        
