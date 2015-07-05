import sys
sys.path.insert(0, ".")
import unittest
from PyOpenWorm import (DataUser, Configureable, BadConf, Configure)
import rdflib
import rdflib as R

from DataTestTemplate import _DataTest


class DataUserTest(_DataTest):

    def test_init_no_config(self):
        """ Should fail to initialize since it's lacking basic configuration """
        c = Configureable.conf
        Configureable.conf = False
        with self.assertRaises(BadConf):
            DataUser()
        Configureable.conf = c

    def test_init_no_config_with_default(self):
        """ Should suceed if the default configuration is a Data object """
        DataUser()

    def test_init_False_with_default(self):
        """ Should suceed if the default configuration is a Data object """
        DataUser(conf=False)

    def test_init_config_no_Data(self):
        """ Should fail if given a non-Data configuration """
        # XXX: This test touches some machinery in
        # PyOpenWorm/__init__.py. Feel like it's a bad test
        tmp = Configureable.conf
        Configureable.conf = Configure()
        with self.assertRaises(BadConf):
            DataUser()
        Configureable.conf = tmp

    @unittest.skip("Should be tracked by version control")
    def test_add_statements_has_uploader(self):
        """ Assert that each statement has an uploader annotation """
        g = R.Graph()

        # Make a statement (triple)
        s = rdflib.URIRef("http://somehost.com/s")
        p = rdflib.URIRef("http://somehost.com/p")
        o = rdflib.URIRef("http://somehost.com/o")

        # Add it to an RDF graph
        g.add((s, p, o))

        # Make a datauser
        du = DataUser(self.config)

        try:
            # Add all of the statements in the graph
            du.add_statements(g)
        except Exception as e:
            self.fail(
                "Should be able to add statements in the first place: " +
                str(e))

        g0 = du.conf['rdf.graph']

        # These are the properties that we should find
        uploader_n3_uri = du.conf['rdf.namespace']['uploader'].n3()
        upload_date_n3_uri = du.conf['rdf.namespace']['upload_date'].n3()

        # This is the query to get uploader information
        q = """
        Select ?u ?t where
        {
        GRAPH ?g
        {
         <http://somehost.com/s>
         <http://somehost.com/p>
         <http://somehost.com/o> .
        }

        ?g """ + uploader_n3_uri + """ ?u.
        ?g """ + upload_date_n3_uri + """ ?t.
        } LIMIT 1
        """
        for x in g0.query(q):
            self.assertEqual(du.conf['user.email'], str(x['u']))

    def test_add_statements_completes(self):
        """ Test that we can upload lots of triples.

        This is to address the problem from issue #31 on https://github.com/openworm/PyOpenWorm/issues
        """
        g = rdflib.Graph()
        for i in range(9000):
            s = rdflib.URIRef("http://somehost.com/s%d" % i)
            p = rdflib.URIRef("http://somehost.com/p%d" % i)
            o = rdflib.URIRef("http://somehost.com/o%d" % i)
            g.add((s, p, o))
        du = DataUser(conf=self.config)
        du.add_statements(g)
