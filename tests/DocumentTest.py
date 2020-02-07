# -*- coding: utf-8 -*-
import unittest
from .DataTestTemplate import _DataTest
from owmeta_core.graph_object import IdentifierMissingException
from owmeta.document import (Document,
                             _doi_uri_to_doi,
                             WormbaseRetrievalException)
import pytest


class DocumentTest(_DataTest):
    ctx_classes = (Document,)

    def test_bibtex_init(self):
        bibtex = u"""@ARTICLE{Cesar2013,
          author = {Jean César},
          title = {An amazing title},
          year = {2013},
          month = jan,
          volume = {12},
          pages = {12--23},
          journal = {Nice Journal},
          abstract = {This is an abstract. This line should be long enough to test
             multilines...},
          comments = {A comment},
          keywords = {keyword1, keyword2},
        }
        """
        self.assertIn(u'Jean César', self.ctx.Document(bibtex=bibtex).author())

    def test_doi_param_sets_id(self):
        doc = Document(doi='blah')
        self.assertIsNotNone(doc.identifier)

    def test_doi_uri_param_sets_id(self):
        doc1 = Document(doi='http://doi.org/blah')
        doc2 = Document(doi='blah')
        self.assertEquals(doc2.identifier, doc1.identifier)

    def test_non_doi_uri_to_doi(self):
        doc = Document(doi='http://example.org/blah')
        self.assertIsNotNone(doc.identifier)


class DOIURITest(unittest.TestCase):
    def test_match(self):
        doi = _doi_uri_to_doi('http://doi.org/blah')
        self.assertEqual('blah', doi)

    def test_nomatch(self):
        doi = _doi_uri_to_doi('http://example.org/blah')
        self.assertIsNone(doi)

    def test_not_a_uri(self):
        doi = _doi_uri_to_doi('10.1098/rstb.1952.0012')
        self.assertIsNone(doi)

    def test_not_doi(self):
        doi = _doi_uri_to_doi('blahblah')
        self.assertIsNone(doi)


@pytest.mark.inttest
class DocumentElaborationTest(_DataTest):
    '''
    Tests for Document 'elaboration', the process of looking up documents from external resources by using their
    identifiers and setting those values on the object
    '''
    ctx_classes = (Document,)

    def test_pubmed_init1(self):
        """
        A pubmed uri
        """
        uri = 'http://www.ncbi.nlm.nih.gov/pubmed/24098140?dopt=abstract'
        doc = self.ctx.Document(pubmed=uri)
        doc.update_from_pubmed()
        self.assertIn(u'Frédéric MY', list(doc.author()))

    def test_pmid_init1(self):
        """
        A pubmed uri doesn't work
        """
        uri = 'http://www.ncbi.nlm.nih.gov/pubmed/24098140?dopt=abstract'
        doc = self.ctx.Document(pmid=uri)
        doc.update_from_pubmed()
        self.assertEqual([], list(doc.author()))

    def test_pmid_init2(self):
        """
        A pubmed id
        """
        pmid = "24098140"
        doc = self.ctx.Document(pmid=pmid)
        doc.update_from_pubmed()
        self.assertIn(u'Frédéric MY', list(doc.author()))

    def test_pubmed_multiple_authors_list(self):
        """
        When multiple authors are on a paper, all of their names should be
        returned in an iterator. Publication order not necessarily preserved
        """
        pmid = "24098140"
        alist = [
            u"Frédéric MY",
            "Lundin VF",
            "Whiteside MD",
            "Cueva JG",
            "Tu DK",
            "Kang SY",
            "Singh H",
            "Baillie DL",
            "Hutter H",
            "Goodman MB",
            "Brinkman FS",
            "Leroux MR"]
        doc = self.ctx.Document(pmid=pmid)
        doc.update_from_pubmed()
        self.assertEqual(set(alist), set(doc.author()))

    def test_wormbase_init(self):
        """ Initialize with wormbase source """
        doc = self.ctx.Document(wormbase="WBPaper00044287")
        doc.update_from_wormbase()
        self.assertIn(u'Frederic MY', list(doc.author()))

    def test_wormbase_year(self):
        for i in range(600, 610):
            wbid = 'WBPaper00044' + str(i)
            doc = self.ctx.Document(wormbase=wbid)
            doc.update_from_wormbase()
            doc.year()

    def test_no_wormbase_id(self):
        doc = self.ctx.Document()
        with self.assertRaises(WormbaseRetrievalException):
            doc.update_from_wormbase()
