from __future__ import absolute_import
import unittest
import os
import subprocess as SP
import tempfile


class ExampleRunnerTest(unittest.TestCase):

    """ Runs the examples to make sure we didn't break the API for them. """

    # Currently these are all failing because we aren't reproducing the actual data that
    # a user gets when they grab the code for the first time

    @classmethod
    def setUpClass(self):
        os.chdir('examples')

    @classmethod
    def tearDownClass(self):
        os.chdir('..')

    def execfile(self, example_file_name):
        fname = tempfile.mkstemp()[1]
        with open(fname, 'w+') as out:
            stat = SP.call(["python", example_file_name],
                           stdout=out,
                           stderr=out)
            out.seek(0)
            self.assertEqual(
                0,
                stat,
                "Example failed with status {}. Its output:\n{}".format(
                    stat,
                    out.read()))
        os.unlink(fname)

    def test_run_NeuronBasicInfo(self):
        self.execfile("NeuronBasicInfo.py")

    def test_run_NetworkInfo(self):
        # XXX: No `synclass' is given, so all neurons are called `excitatory'
        self.execfile("NetworkInfo.py")

    @unittest.expectedFailure
    def test_run_morpho(self):
        self.execfile("morpho.py")

    def test_gap_junctions(self):
        self.execfile("gap_junctions.py")

    def test_add_reference(self):
        self.execfile("add_reference.py")

    def test_bgp(self):
        self.execfile("test_bgp.py")

    @unittest.skip("See #102")
    def test_rmgr(self):
        self.execfile("rmgr.py")
