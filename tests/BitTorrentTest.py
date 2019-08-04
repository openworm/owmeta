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
import six
import sys
import tempfile
from textwrap import dedent
import traceback
import transaction
from pytest import mark, fixture
import unittest

from PyOpenWorm.data_trans.local_file_ds import LocalFileDataSource as LFDS
from PyOpenWorm import connect
from PyOpenWorm.datasource import DataTranslator
from PyOpenWorm.context import Context

class TestBitTorrentDataSourceDirLoader(unittest.TestCase):
    def test_torrent_download1(self):
        self.assertFalse(os.path.exists("d9da5ce947c6f1c127dfcdc2ede63320.torrent"), False)
        self.assertFalse(os.path.exists("Merged_Nuclei_Stained_Worm.zip"), False)
        content = BitTorrentDataSourceDirLoader("./")
        ident = 'http://openworm.org/entities/ConnectomeCSVDataSource/Mark_Arnab_3000_connections'
        content_path = content.load(ident)
        self.assertTrue(os.path.exists("d9da5ce947c6f1c127dfcdc2ede63320.torrent"), True)
        self.assertTrue(os.path.exists("Merged_Nuclei_Stained_Worm.zip"), True)
        # Merged_Nuclei_Stained_Worm.zip will appear but its contents take a while to download
        # watch the progress with - 'watch python3 torrent_cli.py'