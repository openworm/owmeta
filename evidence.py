# -*- coding: utf-8 -*-
"""
Created on Sun Feb 23 17:10:53 2014

@author: slarson
"""

class Evidence:    
    
    def __init__(self):
        self.pmid = []
        self.expr = ''
        
    def add_pmid(self, pmid):
        """ Add a PubMed ID.
        
            :param pmid: A valid PubMed ID
        """
        # Confirm that pmid contains a valid pubmed id
        self.pmid.append(pmid)
        
    
        