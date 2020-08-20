from __future__ import absolute_import
from __future__ import print_function
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch
import os
import tempfile
import shutil
from os.path import join as p
from rdflib.term import URIRef

from owmeta.data_trans.neuron_data import NeuronCSVDataTranslator, NeuronCSVDataSource
from owmeta.neuron import Neuron
from owmeta.document import Document
from owmeta.network import Network
from owmeta.worm import Worm
from owmeta.evidence import Evidence
from .DataTestTemplate import _DataTest


class _Base(_DataTest):
    def setUp(self):
        super(_Base, self).setUp()
        self.startdir = os.getcwd()
        self.testdir = tempfile.mkdtemp(prefix=__name__ + '.')
        os.chdir(self.testdir)
        self.ds = self.context(NeuronCSVDataSource)()
        self.ds.basedir = lambda: self.testdir
        self.cut = self.context(NeuronCSVDataTranslator)()

    def tearDown(self):
        super(_Base, self).tearDown()
        os.chdir(self.startdir)
        shutil.rmtree(self.testdir)


class NeuronCSVDataTranslatorTest(_Base):

    def setUp(self):
        super(NeuronCSVDataTranslatorTest, self).setUp()
        self.process_class(Worm)
        self.process_class(Neuron)
        self.process_class(Network)
        fname = p(self.testdir, 'mycsv.csv')
        text = '''
header,row,completely,ignored,x
ADAR,Neuropeptide,PDF-1,WormAtlas,http://wormatlas.org/neurons/Individual%20Neurons/ADAmainframe.htm'''
        with open(fname, 'w') as f:
            f.write(text.strip())
        self.ds.csv_file_name('mycsv.csv')

    def test_creates_neuron(self):
        res = self.cut(self.ds, output_identifier=URIRef('http://example.org/smashing'))
        n = res.data_context(Neuron)()
        self.assertEqual(len(list(n.load())), 1)

    def test_neuron_name(self):
        res = self.cut(self.ds, output_identifier=URIRef('http://example.org/wonderful'))
        n = res.data_context(Neuron)()
        for o in n.load():
            self.assertEqual(n.name(), 'ADAR')

    def test_neuropeptide(self):
        res = self.cut(self.ds, output_identifier=URIRef('http://example.org/wonderful'))
        n = res.data_context(Neuron)()
        for o in n.load():
            self.assertEqual(n.neuropeptide(), {'PDF-1'})

    def test_evidence(self):
        res = self.cut(self.ds, output_identifier=URIRef('http://example.org/wonderful'))
        ev = res.evidence_context(Evidence)()
        ev.supports(res.data_context.rdf_object)
        for o in ev.load():
            self.assertEqual(o.url(), 'http://wormatlas.org/neurons/Individual%20Neurons/ADAmainframe.htm')

    def test_creates_worm(self):
        res = self.cut(self.ds, output_identifier=URIRef('http://example.org/smashing'))
        n = res.data_context(Worm)()
        self.assertEqual(len(list(n.load())), 1)

    def test_creates_network(self):
        res = self.cut(self.ds, output_identifier=URIRef('http://example.org/smashing'))
        n = res.data_context(Network)()
        self.assertEqual(len(list(n.load())), 1)


class NeuronCSVDataTranslatorNoEvidenceTest(_Base):

    def setUp(self):
        super(NeuronCSVDataTranslatorNoEvidenceTest, self).setUp()
        fname = p(self.testdir, 'mycsv.csv')
        text = '''
header,row,completely,ignored,x
ADAR,Neuropeptide,PDF-1,WormAtlas,'''
        with open(fname, 'w') as f:
            f.write(text.strip())

        self.ds.csv_file_name('mycsv.csv')

    def test_no_evidence(self):
        res = self.cut(self.ds, output_identifier=URIRef('http://example.org/wonderful'))

        ev = res.evidence_context(Evidence)()
        ev.supports(res.data_context.rdf_object)
        self.assertEqual(0, len(list(ev.load())))


class NeuronCSVDataTranslatorBibtexTest(_Base):

    def setUp(self):
        super(NeuronCSVDataTranslatorBibtexTest, self).setUp()
        fname = p(self.testdir, 'mycsv.csv')
        text = '''
header,row,completely,ignored,x
ADAR,Neuropeptide,PDF-1,WormAtlas,'''
        with open(fname, 'w') as f:
            f.write(text.strip())
        self.mapper.add_class(Evidence)
        self.mapper.add_class(Document)
        self.ds.csv_file_name('mycsv.csv')
        self.ds.bibtex_files(['ignored'])
        self.patcher = patch('owmeta.data_trans.neuron_data.parse_bibtex_into_documents')
        mock = self.patcher.start()

        def m(a, ctx):
            return {'WormAtlas': ctx(Document)(key="WormAtlas", title="something")}
        mock.side_effect = m

    def tearDown(self):
        super(NeuronCSVDataTranslatorBibtexTest, self).tearDown()
        self.patcher.stop()

    def test_has_evidence(self):
        res = self.cut(self.ds, output_identifier=URIRef('http://example.org/wonderful'))
        ev = res.evidence_context(Evidence)()
        self.assertEqual(1, len(list(ev.load())))

    def test_evidence_title(self):
        res = self.cut(self.ds, output_identifier=URIRef('http://example.org/wonderful'))
        ev = res.evidence_context(Evidence)()
        for e in ev.load():
            self.assertEqual(e.reference().title(), 'something')
