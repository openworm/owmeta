# -*- coding: utf-8 -*-
from __future__ import absolute_import

from PyOpenWorm.evidence import Evidence
from six.moves.urllib.parse import urlparse

from .DataTestTemplate import _DataTest
import re

# Regular expressions copied from:
# https://www.crossref.org/blog/dois-and-matching-regular-expressions/
DOI_REGEXEN = map(re.compile, (r'/^10.\d{4,9}/[-._;()/:A-Z0-9]+$/i',
                               r'/^10.1002/[^\s]+$/i'))


class EvidenceQualityTests(_DataTest):
    def test_has_valid_resource(self):
        """Checks if the object has either a valid DOI or URL"""
        ev = Evidence()
        allEvidence = set(ev.load())
        qualityEvidence = set()
        for evobj in allEvidence:
            doi = evobj.doi()

            if doi:
                good_doi = False
                for pat in DOI_REGEXEN:
                    if pat.match(doi):
                        good_doi = True
                        break
                if not good_doi:
                    continue

            urls = evobj.uri.get()
            good_uris = True
            for uri in urls:
                parsed = urlparse(uri)
                if not parsed.scheme or not parsed.netloc:
                    good_uris = False
                    break

            if not good_uris:
                continue

            qualityEvidence.add(evobj)

        self.assertSetEqual(allEvidence, qualityEvidence)
