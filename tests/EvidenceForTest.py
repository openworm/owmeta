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
        c1 = Context()
        c1(Neuron)('AVAL').innexin('UNC-7')
        evc = Context()
        ev1 = evc(Evidence)(key='js2019')
        ev1.supports(c1.rdf_object)
        ctx = Context()
        ctx.add_import(c1)
        ctx.add_import(evc)
        ctx.save_context()
        ev_iterable = evidence_for(c1, self.conn)
        self.assertTrue((len(ev_iterable) != 0))
