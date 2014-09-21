import rdflib
import unittest


class DataTest(unittest.TestCase):

    def testUniqueCellNode(self):
        g = rdflib.Graph("ZODB")
        g.parse("out.n3", format="n3")

        qres = g.query(
         """ SELECT ?s ?p
            WHERE {?s ?p "AVAL" } LIMIT 5"""
        )

        for row in qres.result:
            print("%s %s" % row)