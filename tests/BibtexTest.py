from PyOpenWorm.bibtex import parse_bibtex_into_evidence
from os.path import dirname, abspath, join
from .DataTestTemplate import _DataTest


class BibtexTest(_DataTest):

    def test_parse(self):
        basepath = dirname(__file__)
        filepath = abspath(join(basepath, "test_data", "test.bib"))
        bt = parse_bibtex_into_evidence(filepath)
        for x in bt.values():
            self.assertEqual(
                set(x.author()),
                {"Altun, Zeynep F",
                 "Chen, Bojun",
                 "Wang, Zhao-Weng",
                 "Hall, David H"})
