# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
import unittest
import itertools

from .TestUtilities import xfail_without_db
import PyOpenWorm
from PyOpenWorm.context import Context
from PyOpenWorm.neuron import Neuron
from PyOpenWorm.evidence import Evidence
from PyOpenWorm.evidence import evidence_for
from PyOpenWorm import connect, disconnect
from .DataTestTemplate import _DataTest

class EvidenceForTest(_DataTest):
    ''' Tests for statements having an associated Evidence object '''
    def setUp(self):
        # Make the statements and evidence we will query for in the test
        super(EvidenceForTest, self).setUp()
        c1 = Context(ident='http://example.org/statements', conf=self.conf)
        c1(Neuron)('AVAL').innexin('UNC-7')
        evc = Context(ident='http://example.org/metadata', conf=self.conf)
        ev1 = evc(Evidence)(key='js2019')
        ev1.supports(c1.rdf_object)
        # Save them
        c1.save_context()
        evc.save_context()

    def test_retrieve(self):
        # Make the context that holds the statements. The identifier and whether
        # it's connected to a database doesn't matter here: it's just a
        # container for statements
        qctx = Context()
        qctx(Neuron)('AVAL').innexin('UNC-7')

        # Make the context we query statements from. This could be a 'staged'
        # context, but in this case we use what we've written to the IOMemory
        # store provided by _DataTest in self.conf['rdf.graph']
        ctx = Context(conf=self.conf).stored

        # Actually do the query
        ev_iterable = evidence_for(qctx, ctx)

        self.assertEqual(len(ev_iterable), 1)

    def test_statements_with_no_evidence(self):
        # Make the context that holds the statements.
        # These statements were not made in the setUp
        qctx = Context()
        qctx(Neuron)('AVAR').innexin('UNC-7')

        # Make the context we query statements from. This could be a 'staged'
        # context, but in this case we use what we've written to the IOMemory
        # store provided by _DataTest in self.conf['rdf.graph']
        ctx = Context(conf=self.conf).stored

        # Actually do the query
        ev_iterable = evidence_for(qctx, ctx)

        self.assertEqual(len(ev_iterable), 0)

    def test_distinct_evidence_context(self):
        # Make the context that holds the statements.
        qctx = Context()
        qctx(Neuron)('AVAL').innexin('UNC-7')

        # Make the context we query statements from. This could be a 'staged'
        # context, but in this case we use what we've written to the IOMemory
        # store provided by _DataTest in self.conf['rdf.graph']
        ctx = Context(ident='http://example.org/statements', conf=self.conf).stored
        # Make the context that we query Evidence from
        evctx = Context(ident='http://example.org/metadata', conf=self.conf).stored

        # Actually do the query
        ev_iterable = evidence_for(qctx, ctx, evctx)

        self.assertEqual(len(ev_iterable), 1)

    def test_statements_but_no_evidence(self):
        # Make the context that holds the statements.
        qctx = Context()
        qctx(Neuron)('AVAL').innexin('UNC-7')

        # Make the context we query statements from. This could be a 'staged'
        # context, but in this case we use what we've written to the IOMemory
        # store provided by _DataTest in self.conf['rdf.graph']
        ctx = Context(ident='http://example.org/statements', conf=self.conf).stored
        evctx = Context(ident='http://example.org/somerandomcontext', conf=self.conf).stored

        # Actually do the query
        ev_iterable = evidence_for(qctx, ctx, evctx)

        # Verify that there is at least one evidence object returned
        self.assertEqual(len(ev_iterable), 0)
