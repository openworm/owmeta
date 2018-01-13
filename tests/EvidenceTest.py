# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import absolute_import
from .DataTestTemplate import _DataTest
from PyOpenWorm.evidence import Evidence
from PyOpenWorm.dataObject import DataObject


class EvidenceTest(_DataTest):
    ctx_classes = (Evidence,)

    def test_asserts(self):
        """
        Asserting something should allow us to get it back.
        """
        e = Evidence(key='WBPaper00044600')
        r = DataObject(key="context_data_object")
        e.supports(r)
        s = list(e.supports.get())
        self.assertIn(r, s)

    def test_asserts_query(self):
        """ Show that we can store the evidence on an object and later retrieve it """
        e = self.ctx.Evidence(key="a")
        r = DataObject(key="relationship")
        e.supports(r)
        self.save()
        e0 = self.ctx.Evidence()
        e0.supports(r)
        s = list(e0.load())
        self.assertIn(e, s)

    def test_asserts_query_multiple(self):
        """ Show that setting the evidence with distinct objects yields
            distinct results """
        r = DataObject(key='relationship')
        ar = DataObject(key='aref')
        br = DataObject(key='bref')

        e = self.ctx.Evidence(key="a", reference=ar)
        e.supports(r)
        self.save()

        e1 = self.ctx.Evidence(key="b", reference=br)
        e1.supports(r)
        self.save()

        e0 = Evidence()
        e0.supports(r)
        for x in e0.load():
            lar = x.reference.one()
            lbr = x.reference.one()
            # Testing that either a has a result tom@cn.com and y has nothing or
            # y has a result 1999 and a has nothing
            if x.idl == e1.idl:
                self.assertEqual(lbr, br)
            elif x.idl == e.idl:
                self.assertEqual(lar, ar)
            else:
                self.fail("Unknown object returned from load")


class Issue211EvidenceTest(_DataTest):
    """
    Can we assert the same fact with two distinct pieces of Evidence?

    issue: openworm/PyOpenWorm#211

    """

    def setUp(self):
        super(Issue211EvidenceTest, self).setUp()
        self.e1 = Evidence()
        self.e2 = Evidence()

        c = DataObject(key=23)
        self.e1.supports(c)
        self.e2.supports(c)
        self.evs = Evidence()
        self.evs.supports(c)

        self.expected_ids = set(['777', '888'])

    def assertEvidences(self, prop):
        getattr(self.e1, prop)('777')
        getattr(self.e2, prop)('888')
        self.save()
        self.save()
        loaded_ids = set(getattr(self.evs, prop).get())
        self.assertTrue(self.expected_ids.issubset(loaded_ids))

    def test_multiple_pmid_evidence_for_single_fact(self):
        self.assertEvidences('pmid')

    def test_multiple_doi_evidence_for_single(self):
        self.assertEvidences('doi')

    def test_multiple_wbid_evidence_for_single(self):
        self.assertEvidences('wbid')

    def test_multiple_uri_evidence_for_single(self):
        self.assertEvidences('uri')
