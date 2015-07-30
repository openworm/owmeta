# -*- coding: utf-8 -*-
import sys
sys.path.insert(0,".")
import unittest
import neuroml
import neuroml.writers as writers
import PyOpenWorm
from PyOpenWorm import *
import networkx
import rdflib
import rdflib as R
import pint as Q
import os
import subprocess as SP
import subprocess
import tempfile
import doctest

from glob import glob

from GraphDBInit import *

from DataTestTemplate import _DataTest

class EvidenceTest(_DataTest):
    @unittest.skip("Post alpha")
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
        self.assertEqual(u"Jean César", next(Evidence(bibtex=bibtex).author()))

    def test_pubmed_init1(self):
        """
        A pubmed uri
        """
        uri = "http://www.ncbi.nlm.nih.gov/pubmed/24098140?dopt=abstract"
        self.assertIn(u"Frédéric MY", list(Evidence(pmid=uri).author()))

    def test_pubmed_init2(self):
        """
        A pubmed id
        """
        pmid = "24098140"
        self.assertIn(u"Frédéric MY", list(Evidence(pmid=pmid).author()))

    def test_pubmed_multiple_authors_list(self):
        """
        When multiple authors are on a paper, all of their names should be returned in an iterator. Publication order not necessarily preserved
        """
        pmid = "24098140"
        alist = [u"Frédéric MY","Lundin VF","Whiteside MD","Cueva JG","Tu DK","Kang SY","Singh H","Baillie DL","Hutter H","Goodman MB","Brinkman FS","Leroux MR"]
        self.assertEqual(set(alist), set(Evidence(pmid=pmid).author()))

    @unittest.skip("Fix later")
    def test_doi_init_fail_on_request_prefix(self):
        """
        Requesting only the prefix
        """
        with self.assertRaises(EvidenceError):
            Evidence(doi='http://dx.doi.org/10.1126')

    @unittest.skip("Fix later")
    def test_doi_init_fail_on_request_suffix(self):
        """
        Requesting only the prefix
        """
        with self.assertRaises(EvidenceError):
            Evidence(doi='http://dx.doi.org/s00454-010-9273-0')

    def test_wormbase_init(self):
        """ Initialize with wormbase source """
        # Wormbase lacks anything beyond the author,date format for a lot of papers
        self.assertIn(u'Frederic et al., 2013', list(Evidence(wormbase="WBPaper00044287").author()))

    def test_wormbase_year(self):
        """ Just make sure we can extract something without crashing """
        for i in range(600,610):
            wbid = 'WBPaper00044' + str(i)
            e = Evidence(wormbase=wbid)
            e.year()

    def test_asserts(self):
        """
        Asserting something should allow us to get it back.
        """
        e=Evidence(wormbase='WBPaper00044600')
        g = make_graph(20)
        r = Relationship(graph=g)
        e.asserts(r)
        r.identifier = lambda **args : r.make_identifier("test")
        e.save()
        l = list(e.asserts())
        self.assertIn(r,l)

    def test_asserts_query(self):
        """ Show that we can store the evidence on an object and later retrieve it """
        e = Evidence(author='tom@cn.com')
        r = Relationship(make_graph(10))
        e.asserts(r)
        e.save()
        e0 = Evidence()
        e0.asserts(r)
        s = list(e0.load())
        author = s[0].author.one()
        self.assertIn('tom@cn.com', author)

    def test_asserts_query_multiple(self):
        """ Show that setting the evidence with distinct objects yields
            distinct results """
        e = Evidence(author='tom@cn.com')
        r = Relationship(make_graph(10))
        e.asserts(r)
        e.save()

        e1 = Evidence(year=1999)
        e1.asserts(r)
        e1.save()

        e0 = Evidence()
        e0.asserts(r)
        for x in e0.load():
            a = x.author.one()
            y = x.year()
            # Testing that either a has a result tom@cn.com and y has nothing or
            # y has a result 1999 and a has nothing
            self.assertTrue(a == 'tom@cn.com' and int(y) == 1999)

    def test_asserts_query_multiple_author_matches(self):
        """ Show that setting the evidence with distinct objects yields
        distinct results even if there are matching values """
        e = Evidence(author='tom@cn.com')
        r = Relationship(make_graph(10))
        e.asserts(r)
        e.save()

        e1 = Evidence(author='tom@cn.com')
        e1.asserts(r)
        e1.save()

        e0 = Evidence()
        e0.asserts(r)
        self.assertTrue(len(list(e0.load())) == 2)

    def test_evidence_retrieves_instead_of_overwrites(self):
        """
        Test that creating a new Evidence with the same attributes of an
        already-saved Evidence does not overwrite the previous Evidence,
        but instead retrieves it.
        """
        e = Evidence(author='Rodney Dangerfield')
        r = Relationship(make_graph(10))
        e.asserts(r)
        e.save()

        e1 = Evidence(author='Rodney Dangerfield')
        facts = list(e1.asserts())
        assert facts[0] == r

    @unittest.expectedFailure
    def test_multiple_evidence_for_single_fact(self):
        """
        Can we assert the same fact with two distinct pieces of Evidence?
        """

        e1 = Evidence()
        e1.pmid('777')

        e2 = Evidence()
        e2.pmid('888')

        c = Channel()   # using a Channel here, but it could be any fact...
        e1.asserts(c)
        e2.asserts(c)

        e1.save()
        e2.save()

        evs = Evidence()
        evs.asserts(c.description)

        saved_pmids = set(['777', '888'])
        loaded_pmids = set([x.pmid() for x in evs.load()])

        assert saved_pmids.issubset(loaded_pmids)

