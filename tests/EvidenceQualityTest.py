# -*- coding: utf-8 -*-
from __future__ import absolute_import
import unittest
from PyOpenWorm.evidence import Evidence
import requests

from .DataTestTemplate import _DataTest


class EvidenceQualityTests(_DataTest):
    @unittest.expectedFailure
    def test_has_valid_resource(self):
        """Checks if the object has either a valid DOI or URL"""
        ev = Evidence()
        allEvidence = list(ev.load())
        evcheck = []
        for evobj in allEvidence:
            if evobj.doi():
                doi = evobj.doi()
                val = requests.get('http://dx.doi.org/' + doi)
                evcheck.append(val.status_code == 200)

            elif evobj.url():
                url = evobj.url()
                val = requests.get(url)
                evcheck.append(val.status_code == 200)

            else:
                evcheck.append(False)

        self.assertTrue(False not in evcheck)

    @unittest.expectedFailure
    def test_resource_alignment(self):
        """Checks that DOI and URL fields are aligned,
        when both are present"""
        ev = Evidence()
        allEvidence = list(ev.load())
        evcheck = []
        for evobj in allEvidence:
            if evobj.doi() and evobj.url():
                doi = evobj.doi()
                doival = requests.get('http://dx.doi.org/' + doi)
                url = evobj.url()
                urlval = requests.get(url)
                evcheck.append(doival.status_code == urlval.status_code)

        self.assertTrue(False not in evcheck)
