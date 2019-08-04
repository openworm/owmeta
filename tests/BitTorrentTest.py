# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
import unittest
import itertools
from .TestUtilities import xfail_without_db
import PyOpenWorm
from .DataTestTemplate import _DataTest
from PyOpenWorm.bittorrent import BitTorrentDataSourceDirLoader
import os
from os.path import exists, join as p
import six
import sys
import tempfile
from textwrap import dedent
import traceback
import transaction
from pytest import mark, fixture
import unittest
import shutil

from PyOpenWorm.data_trans.local_file_ds import LocalFileDataSource as LFDS
from PyOpenWorm import connect
from PyOpenWorm.datasource import DataTranslator
from PyOpenWorm.context import Context
import transaction


class TestBitTorrentDataSourceDirLoader(_DataTest):
    def setUp(self):
        super(TestBitTorrentDataSourceDirLoader, self).setUp()
        self.ident = 'http://openworm.org/entities/ConnectomeCSVDataSource/Mark_Arnab_3000_connections'
        with transaction.manager:
            # Create data sources
            ctx = Context(ident='http://example.org/context', conf=self.connection.conf)
            ctx(LFDS)(
                ident=self.ident,
                file_name='Merged_Nuclei_Stained_Worm.zip',
                torrent_file_name='d9da5ce947c6f1c127dfcdc2ede63320.torrent'
            )
            ctx.save_context()
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_torrent_download1(self):
        ctx = Context(ident="http://example.org/context", conf=self.connection.conf)
        self.assertFalse(exists(p(self.tempdir, "d9da5ce947c6f1c127dfcdc2ede63320.torrent")), False)
        self.assertFalse(exists(p(self.tempdir, "Merged_Nuclei_Stained_Worm.zip")), False)

        content = BitTorrentDataSourceDirLoader(self.tempdir, powdir='.pow', tempdir=self.tempdir)

        for m in ctx.stored(LFDS)(ident=self.ident).load():
            print("GOT", m)
            content_path = content.load(m)

        self.assertTrue(exists(p(self.tempdir, "d9da5ce947c6f1c127dfcdc2ede63320.torrent")), True)
        self.assertTrue(exists(p(self.tempdir, "Merged_Nuclei_Stained_Worm.zip")), True)
        # Merged_Nuclei_Stained_Worm.zip will appear but its contents take a while to download
        # watch the progress with - 'watch python3 torrent_cli.py'
