# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import absolute_import

from owmeta_core.dataObject import DataObject
from owmeta_core.configure import Configureable

from owmeta.evidence import Evidence

from .DataTestTemplate import _DataTest

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


class EvidenceTest(_DataTest):
    ctx_classes = (Evidence,)

    def setUp(self):
        self.patcher = patch('owmeta_core.data', 'ALLOW_UNCONNECTED_DATA_USERS', True)
        self.patcher.start()
        super(EvidenceTest, self).setUp()

    def tearDown(self):
        super(EvidenceTest, self).tearDown()
        self.patcher.stop()

    def test_asserts(self):
        """
        Asserting something should allow us to get it back.
        """
        e = self.ctx.Evidence(key='WBPaper00044600')
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

        e0 = self.ctx.Evidence()
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

    issue: openworm/owmeta#211

    """

    ctx_classes = (Evidence,)

    def setUp(self):
        super(Issue211EvidenceTest, self).setUp()
        self.e1 = self.ctx.Evidence()
        self.e2 = self.ctx.Evidence()

        c = DataObject(key='23')
        self.e1.supports(c)
        self.e2.supports(c)
        self.evs = self.context.stored(Evidence)()
        self.evs.supports(c)

        self.expected_ids = set(['777', '888'])

    def test_references(self):
        self.e1.reference(DataObject(ident='777'))
        self.e2.reference(DataObject(ident='888'))
        self.save()
        loaded_ids = set(str(x.identifier) for x in self.evs.reference.get())
        self.assertTrue(self.expected_ids.issubset(loaded_ids))
