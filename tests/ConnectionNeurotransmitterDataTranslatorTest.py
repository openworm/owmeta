from __future__ import absolute_import
from __future__ import print_function
from textwrap import dedent
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch
import os
import tempfile
import shutil
from os.path import join as p
from rdflib.term import URIRef

from owmeta.data_trans.data_with_evidence_ds import DataWithEvidenceDataSource
from owmeta.data_trans.connections import (NeuronConnectomeSynapseClassTranslator,
                                           ConnectomeCSVDataSource)
from owmeta.neuron import Neuron
from owmeta.connection import Connection
from owmeta_core.context import IMPORTS_CONTEXT_KEY
from .DataTestTemplate import _DataTest


class _Base(_DataTest):
    def setUp(self):
        super(_Base, self).setUp()
        self.conf[IMPORTS_CONTEXT_KEY] = 'http://example.org/imports_context'
        self.startdir = os.getcwd()
        self.testdir = tempfile.mkdtemp(prefix=__name__ + '.')
        os.chdir(self.testdir)
        self.conn_ds = self.context(DataWithEvidenceDataSource)(key='test_dweds')
        self.nt_ds = self.context(ConnectomeCSVDataSource)()
        self.nt_ds.basedir = lambda: self.testdir
        self.cut = self.context(NeuronConnectomeSynapseClassTranslator)()

    def tearDown(self):
        super(_Base, self).tearDown()
        os.chdir(self.startdir)
        shutil.rmtree(self.testdir)


class InexactNumberMatchTest(_Base):

    def setUp(self):
        super(InexactNumberMatchTest, self).setUp()
        fname = p(self.testdir, 'mycsv.csv')
        text = 'PreCell;PostCell;send;3;neurotransmitter'
        with open(fname, 'w') as f:
            f.write(text)
        self.nt_ds.csv_file_name('mycsv.csv')
        self.conn_ds.data_context(Connection)(pre_cell=Neuron('PreCell'),
                                              post_cell=Neuron('PostCell'),
                                              syntype='send')
        self.conn_ds.commit()

    def test_connection_exists(self):
        res = self.cut(self.conn_ds, self.nt_ds)
        res.commit()
        conn = res.data_context.stored(Connection).query()
        self.assertEqual(len(list(conn.load())), 1)

    def test_adds_nt(self):
        res = self.cut(self.conn_ds, self.nt_ds)
        res.commit()
        conn = res.data_context.stored(Connection).query()
        self.assertEqual(list(conn.load())[0].synclass(), 'neurotransmitter')


class ExactNumberMatchTest(_Base):

    def setUp(self):
        super(ExactNumberMatchTest, self).setUp()
        fname = p(self.testdir, 'mycsv.csv')
        text = 'PreCell;PostCell;send;3;neurotransmitter'
        with open(fname, 'w') as f:
            f.write(text)
        self.nt_ds.csv_file_name('mycsv.csv')
        self.conn_ds.data_context(Connection)(pre_cell=Neuron('PreCell'),
                                              post_cell=Neuron('PostCell'),
                                              syntype='send',
                                              number=3)
        self.conn_ds.commit()

    def test_connection_exists(self):
        res = self.cut(self.conn_ds, self.nt_ds)
        res.commit()
        conn = res.data_context.stored(Connection).query()
        self.assertEqual(len(list(conn.load())), 1)

    def test_adds_nt(self):
        res = self.cut(self.conn_ds, self.nt_ds)
        res.commit()
        conn = res.data_context.stored(Connection).query()
        self.assertEqual(list(conn.load())[0].synclass(), 'neurotransmitter')
