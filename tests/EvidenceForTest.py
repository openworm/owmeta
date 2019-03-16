# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
import unittest
import itertools

from .TestUtilities import xfail_without_db
import PyOpenWorm
from PyOpenWorm.context import Context
from PyOpenWorm.neuron import Neuron
from PyOpenWorm.worm import Worm
from PyOpenWorm.evidence import Evidence
from PyOpenWorm.evidence import evidence_for
from PyOpenWorm import connect, disconnect

# XXX: This could probably just be one test at this point -- iterate over all contexts and check for an
# Evidence:supports triple
class EvidenceForTest(unittest.TestCase):
    ''' Tests for statements having an associated Evidence object '''
    def setUp(self):
        xfail_without_db()
        self.conn = PyOpenWorm.connect('readme.conf')
        self.g = self.conn.conf["rdf.graph"]
        self.context = Context()
        self.qctx = self.context.stored

    def tearDown(self):
        PyOpenWorm.disconnect(self.conn)

    def test_evidence_for(self):
        qctx = Context()
        qctx(Neuron)('AVAL').innexin('UNC-7')
        ev_iterable = evidence_for(qctx, self.conn, Evidence, Context)
        self.assertTrue((len(ev_iterable) != 0))