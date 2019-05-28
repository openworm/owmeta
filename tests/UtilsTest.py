# -*- coding: utf-8 -*-
import unittest
from PyOpenWorm.utils import ellipsize


class EllipsizeTest(unittest.TestCase):

    def test_nochange_eq(self):
        t = 'sad'
        self.assertEqual(ellipsize(t, 3), t)

    def test_force_no_ellipsis(self):
        t = 'sad'
        self.assertEqual(ellipsize(t, 1), t[:1])

    def test_nochange_longer(self):
        t = 'sad'
        self.assertEqual(ellipsize(t, 4), t)

    def test_nochange_longer(self):
        t = 'sudan'
        self.assertEqual(ellipsize(t, 4), 'sud…')

    def test_nochange_empty(self):
        t = ''
        self.assertEqual(ellipsize(t, 80), '')

    def test_truncate(self):
        t = 'some random string'
        self.assertEqual(ellipsize(t, 0), '')
