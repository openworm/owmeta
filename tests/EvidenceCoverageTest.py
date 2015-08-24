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

from GraphDBInit import *

from DataTestTemplate import _DataTest

class EvidenceCoverageTest(_DataTest):

    def test_verify_neurons_have_evidence(self):
        """ For each neuron in PyOpenWorm, verify
        that there is supporting evidence"""
        net = Worm().neuron_network()
        neurons = list(net.neurons())
        evcheck = []
        for n in neurons:
            hasEvidence = len(get_supporting_evidence(n))
            evcheck.append(hasEvidence)
            hasEvidence = len(get_supporting_evidence(n.neurotransmitter))
            evcheck.append(hasEvidence)
            hasEvidence = len(get_supporting_evidence(n.type))
            evcheck.append(hasEvidence)
            hasEvidence = len(get_supporting_evidence(n.innexin))
            evcheck.append(hasEvidence)
            hasEvidence = len(get_supporting_evidence(n.neuropeptide))
            evcheck.append(hasEvidence)
            hasEvidence = len(get_supporting_evidence(n.receptor))
            evcheck.append(hasEvidence)

        self.assertTrue(0 not in evcheck)

    @unittest.expectedFailure
    def test_verify_muslces_have_evidence(self):
        """ For each muscle in PyOpenWorm, verify
        that there is supporting evidence"""
        muscles = list(Worm().muscles())
        muscle_evcheck = []
        for mobj in muscles:
            hasEvidence = len(get_supporting_evidence(mobj))
            muscle_evcheck.append(hasEvidence)

        self.assertTrue(0 not in muscle_evcheck)

    @unittest.expectedFailure
    def test_verify_connections_have_evidence(self):
        """ For each connection in PyOpenWorm, verify that there is
        supporting evidence. """
        net = Worm().neuron_network()
        connections = list(net.synapses())
        evcheck = []
        for c in connections:
            has_evidence = len(get_supporting_evidence(c))
            evcheck.append(has_evidence)

        self.assertTrue(0 not in evcheck)

    @unittest.skip('There is no information at present about channels')
    def test_verify_channels_have_evidence(self):
        """ For each channel in PyOpenWorm, verify that there is
        supporting evidence. """
        pass

    def get_supporting_evidence(fact):
        """ Helper function for checking amount of Evidence.
        Returns list of Evidence supporting fact. """
        ev = Evidence()
        ev.asserts(fact)
        return list(ev.load())
