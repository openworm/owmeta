from __future__ import print_function
import unittest
from unittest.mock import Mock, ANY
from rdflib.term import URIRef
from owmeta_core.command import GenericUserError
from owmeta_core.contextDataObject import ContextDataObject

from owmeta.data_trans.data_with_evidence_ds import DataWithEvidenceDataSource as DWEDS
from owmeta.command import OWMEvidence
from owmeta.document import Document
from owmeta.website import Website


class OWMEvidenceGetDWEDSTest(unittest.TestCase):
    def setUp(self):
        self.parent = Mock(name='parent')
        self.cut = OWMEvidence(self.parent)

        dweds = DWEDS()
        dweds.evidence_context = Mock()
        # load from the given identifier is a dweds
        self.parent._default_ctx.stored(ANY).query().load.return_value = [dweds]
        # load evidence from the evidence_context is just one evidence object
        self.ev_load = dweds.evidence_context.stored(ANY).query().load

    def test_doc(self):
        # given
        evid = Mock(name='evidence')
        doc = Document()
        self.ev_load.return_value = [evid]
        evid.reference.return_value = doc

        # when
        self.cut.get(URIRef('http://example.org/context'))

        # then
        self.ev_load.assert_called()
        self.parent.message.assert_called()

    def test_no_evidence(self):
        '''
        There's no evidence, so we shouldn't see any output
        '''
        # given
        self.ev_load.return_value = []

        # when
        self.cut.get(URIRef('http://example.org/context'))

        # then
        self.parent.message.assert_not_called()

    def test_no_type_resolved(self):
        '''
        There's no evidence, so we shouldn't see any output
        '''
        # given
        self.parent._default_ctx.stored.resolve_class.return_value = None
        self.parent._default_ctx.stored.side_effect = lambda x: x
        self.parent._den3.side_effect = lambda x: x
        # then
        with self.assertRaisesRegexp(GenericUserError, r'unresolved'):
            # when
            self.cut.get(URIRef('http://example.org/context'), rdf_type='unresolved')


class OWMEvidenceGetContextTest(unittest.TestCase):
    def setUp(self):
        self.parent = Mock(name='parent')
        self.cut = OWMEvidence(self.parent)

    def test_doc(self):
        # given
        evid = Mock(name='evidence')
        doc = Document()
        cdo = ContextDataObject()
        # load from the given identifier is a ContextDataObject
        self.parent._default_ctx.stored(ANY).query().load.side_effect = [[cdo],
                                                                      [evid]]
        evid.reference.return_value = doc

        # when
        self.cut.get(URIRef('http://example.org/context'))

        # then
        self.parent.message.assert_called()

    def test_web(self):
        # given
        evid = Mock(name='evidence')
        web = Website()
        cdo = ContextDataObject()
        # load from the given identifier is a ContextDataObject
        self.parent._default_ctx.stored(ANY).query().load.side_effect = [[cdo],
                                                                      [evid]]
        evid.reference.return_value = web

        # when
        self.cut.get(URIRef('http://example.org/context'))

        # then
        self.parent.message.assert_called()

    def test_no_evidence(self):
        '''
        There's no evidence, so we shouldn't see any output
        '''
        # given
        cdo = ContextDataObject()
        self.parent._default_ctx.stored(ANY).query().load.side_effect = [[cdo],
                                                                      []]

        # when
        self.cut.get(URIRef('http://example.org/context'))

        # then
        self.parent.message.assert_not_called()
