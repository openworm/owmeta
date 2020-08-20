# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

from owmeta_core.context import Context
from owmeta.neuron import Neuron
from owmeta.evidence import Evidence
from owmeta.evidence import evidence_for
from .DataTestTemplate import _DataTest


class EvidenceForTest(_DataTest):
    ''' Tests for statements having an associated Evidence object '''
    def setUp(self):
        # Make the statements and evidence we will query for in the test
        super(EvidenceForTest, self).setUp()
        self.process_class(Evidence)
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
        ctx = self.connection(Context)().stored

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
        ctx = self.connection(Context)().stored

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
        ctx = self.connection(Context)(ident='http://example.org/statements').stored
        # Make the context that we query Evidence from
        evctx = self.connection(Context)(ident='http://example.org/metadata').stored

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
        ctx = self.connection(Context)(ident='http://example.org/statements').stored
        evctx = self.connection(Context)(ident='http://example.org/somerandomcontext').stored

        # Actually do the query
        ev_iterable = iter(evidence_for(qctx, ctx, evctx))

        # Verify that there is at least one evidence object returned
        ev = next(ev_iterable, None)
        self.assertEqual(ev, None)
