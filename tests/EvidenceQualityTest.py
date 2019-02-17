# -*- coding: utf-8 -*-
from __future__ import absolute_import

from .DataTestTemplate import _DataTest
import PyOpenWorm
from PyOpenWorm.evidence import Evidence
from PyOpenWorm.document import Document
from PyOpenWorm.website import Website
from PyOpenWorm.context import Context
from six.moves.urllib.parse import urlparse
import pytest

import re

# Regular expressions copied from:
# https://www.crossref.org/blog/dois-and-matching-regular-expressions/
DOI_REGEXEN = [re.compile(x, re.I) for x in (r'^10.\d{4,9}/[-._;()/:A-Z0-9]+$',
                                             r'^10.1002/\S+$')]


@pytest.mark.inttest
class EvidenceQualityTests(_DataTest):
    '''
    Tests for the quality of evidence. As distinct from coverage, these test things like whether accession information
    is included and usable, whether certain fields are properly formatted, etc.
    '''

    def setUp(self):
        self.conn = PyOpenWorm.connect(configFile='tests/data_integrity_test.conf')
        self.g = self.conn.conf["rdf.graph"]
        self.context = Context()
        self.qctx = self.context.stored

    def tearDown(self):
        PyOpenWorm.disconnect(self.conn)

    def test_has_valid_resource(self):
        """Checks if the object has either a valid DOI or URL"""
        ev = self.qctx(Evidence)()
        allEvidence = set(ev.load())
        qualityEvidence = set()
        for evobj in allEvidence:
            ref = evobj.reference()
            if isinstance(ref, Document):
                doi = ref.doi()
                if doi:
                    for pat in DOI_REGEXEN:
                        if pat.match(doi):
                            qualityEvidence.add(evobj)
                            break
                    else: # no break
                        continue

                urls = ref.uri.get()
                good_uris = True
                for uri in urls:
                    parsed = urlparse(uri)
                    if not parsed.scheme or not parsed.netloc:
                        good_uris = False
                        break

                if not good_uris:
                    continue
            elif isinstance(ref, Website):
                urls = ref.url.get()
                urls = list(urls)
                print(urls)
                good_uris = True
                for uri in urls:
                    parsed = urlparse(uri)
                    if not parsed.scheme or not parsed.netloc:
                        good_uris = False
                        break

                if not good_uris:
                    continue
            qualityEvidence.add(evobj)

        self.assertSetEqual(allEvidence, qualityEvidence,
                            msg='\n'.join(str(x.reference()) for x in (allEvidence - qualityEvidence)))
