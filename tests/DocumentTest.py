# -*- coding: utf-8 -*-
from .DataTestTemplate import _DataTest
from PyOpenWorm.document import Document
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
        """ Just make sure we can extract something without crashing """
        for i in range(600, 610):
            wbid = 'WBPaper00044' + str(i)
            doc = self.ctx.Document(wormbase=wbid)
            doc.update_from_wormbase()
            doc.year()
