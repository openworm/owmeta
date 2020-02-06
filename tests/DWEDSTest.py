from __future__ import absolute_import
from __future__ import print_function
import unittest

from owmeta_core.contextDataObject import ContextDataObject
from rdflib.term import URIRef

from owmeta.data_trans.data_with_evidence_ds import DataWithEvidenceDataSource


class DataWithEvidenceDataSourceTest(unittest.TestCase):
    def test_init_with_args(self):
        m = ContextDataObject(ident=URIRef('http://example.org/my-evidence'))
        cut = DataWithEvidenceDataSource(ident=URIRef('http://example.org/dweds6'),
                                         evidence_context_property=m)
        self.assertEqual(m, cut.evidence_context_property.onedef())

    def test_init_context_properties(self):
        cut = DataWithEvidenceDataSource(ident=URIRef('http://example.org/dweds6'))
        self.assertIsNotNone(cut.evidence_context_property.onedef())
