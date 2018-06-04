import unittest
try:
    from unittest.mock import Mock, ANY
except ImportError:
    from mock import Mock, ANY
import tempfile
from PyOpenWorm.command import POW, UnreadableGraphException
import os
from os.path import exists, abspath
import shutil
import json
from rdflib.term import URIRef


class CommandTest(unittest.TestCase):

    def setUp(self):
        self.testdir = tempfile.mkdtemp(prefix=__name__)
        self.startdir = os.getcwd()
        os.chdir(self.testdir)
        self.cut = POW()

    def tearDown(self):
        os.chdir(self.startdir)
        shutil.rmtree(self.testdir)

    def test_init_default_creates_store(self):
        self.cut.init()
        self.assertTrue(exists('worm.db'), msg='worm.db is created')

    def test_init_default_creates_config(self):
        self.cut.init()
        self.assertTrue(exists('pow.conf'), msg='pow.conf is created')

    def test_init_default_store_name_is_absolute(self):
        self.cut.init()
        with open('pow.conf', 'r') as f:
            conf = json.load(f)
            self.assertTrue(conf['rdf.store_conf'].startswith('/'), msg="DB Store is absolute")

    def test_init_default_store_config_file_exists_no_change(self):
        with open('pow.conf', 'w') as f:
            f.write('{}')

        self.cut.init()
        with open('pow.conf', 'r') as f:
            self.assertEqual('{}', f.read())

    def test_init_default_store_config_file_exists_update_store_conf(self):
        with open('pow.conf', 'w') as f:
            f.write('{}')

        self.cut.init(update_existing_config=True)
        with open('pow.conf', 'r') as f:
            conf = json.load(f)
            self.assertEqual(conf['rdf.store_conf'], abspath('worm.db'), msg='path is updated')

    def test_fetch_graph_no_accessor_finder(self):
        with self.assertRaises(Exception):
            self.cut.fetch_graph("http://example.org/ImAGraphYesSiree")

    def test_fetch_graph_no_accessor(self):
        with self.assertRaises(UnreadableGraphException):
            self.cut.graph_accessor_finder = lambda url: None
            self.cut.fetch_graph("http://example.org/ImAGraphYesSiree")

    def test_fetch_graph_with_accessor_success(self):
        m = Mock()
        self.cut.graph_accessor_finder = lambda url: m
        self.cut.fetch_graph("http://example.org/ImAGraphYesSiree")
        m.assert_called_with()

    def test_add_graph_success(self):
        m = Mock()
        q = (URIRef('http://example.org/s'), URIRef('http://example.org/p'), URIRef('http://example.org/o'), URIRef('http://example.org/c'))
        m().quads.return_value = [q]
        with open('pow.conf', 'w') as f:
            json.dump({'rdf.store': 'default'}, f)
            f.flush()

        self.cut.graph_accessor_finder = lambda url: m
        self.cut.add_graph("http://example.org/ImAGraphYesSiree")
        self.assertIn(q, self.cut._conf()['rdf.graph'])
