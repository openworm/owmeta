''' Tests for the bibtexparser wrapper and related utilities (e.g., translation into Document) '''
from .DataTestTemplate import _DataTest
from PyOpenWorm.bibtex import parse_bibtex_into_evidence, loads
from os.path import dirname, abspath, join
# import logging


# logging.basicConfig(level=logging.DEBUG)


class BibtexTest(_DataTest):
    def loads(self, s):
        for x in loads(s).entries:
            return x

    def test_entrytype_not_listified(self):
        bibtex = u"""@ARTICLE{ex,
          author = "http://example.org",
        }
        """
        bt = self.loads(bibtex)
        self.assertEqual(bt['ENTRYTYPE'], 'article')

    def test_id_not_listified(self):
        bibtex = u"""@ARTICLE{ex,
          author = "http://example.org",
        }
        """
        bt = self.loads(bibtex)
        self.assertEqual(bt['ID'], 'ex')

    def test_parse(self):
        basepath = dirname(__file__)
        filepath = abspath(join(basepath, "test_data", "test.bib"))
        bt = parse_bibtex_into_evidence(filepath)
        for x in bt.values():
            self.assertEqual(
                set(x.reference().author()),
                {"Altun, Zeynep F",
                 "Chen, Bojun",
                 "Wang, Zhao-Weng",
                 "Hall, David H"})

    def test_parse_double_quotes(self):
        bibtex = u"""@ARTICLE{ex,
          author = "http://example.org",
        }
        """
        bt = self.loads(bibtex)
        self.assertEqual(list(bt['author']), ['http://example.org'])

    def test_parse_url_1(self):
        bibtex = u"""@ARTICLE{ex,
          url = {http://example.org}
        }
        """
        bt = self.loads(bibtex)
        self.assertEqual(list(bt['url']), ['http://example.org'])

    def test_parse_url_2(self):
        bibtex = u"""@ARTICLE{ex01,
          url = {http://example.org}
        }
        """
        bt = self.loads(bibtex)
        self.assertEqual(list(bt['url']), ['http://example.org'])

    def test_parse_doi_doi(self):
        bibtex = u"""@ARTICLE{ex01,
          doi = {10.102/blah}
        }
        """
        bt = self.loads(bibtex)
        self.assertEqual(list(bt['url']), ['http://dx.doi.org/10.102/blah'])

    def test_parse_multiple_url_1(self):
        bibtex = r"""@ARTICLE{ex01,
          note = "\url{http://example.org/01} \url{http://example.org/02}"
        }
        """
        bt = self.loads(bibtex)
        self.assertEqual(list(bt['url']), ['http://example.org/01', 'http://example.org/02'])
