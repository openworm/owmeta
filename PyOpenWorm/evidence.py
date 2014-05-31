# -*- coding: utf-8 -*-
"""
Created on Sun Feb 23 17:10:53 2014

@author: slarson
"""

class Evidence(DataUser):

    def __init__(self,reference_url):
        self.pmid = []
        self.expr = ''

    def add_pmid(self, pmid):
        """ Add a PubMed ID.

            :param pmid: A valid PubMed ID
        """
        # Confirm that pmid contains a valid pubmed id
        self.pmid.append(pmid)

    def asserts(self,stmt):
        stmt = tuple(x.identifier() for x in stmt[:3])
        update_stmt = "insert data { _:stmt ns1:subject <%s> ; ns1:predicate <%s> ; ns1:object <%s> ; ns1:asserts }"
        self.conf['rdf.graph'].update(
