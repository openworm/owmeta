from __future__ import absolute_import
from .DataTestTemplate import _DataTest
from PyOpenWorm.experiment import Experiment
from PyOpenWorm.data import DataUser


class ExperimentTest(_DataTest):

    def test_data_user(self):
        """
        Test that the Experiment object is a DataUser object as well.
        """
        do = Experiment('', conf=self.config)
        self.assertTrue(isinstance(do, DataUser))

    def test_unimplemented_conditions(self):
        """
        Test that an Experiment with no conditions attribute raises an
        error when get_conditions() is called.
        """
        ex = Experiment()
        with self.assertRaises(NotImplementedError):
            ex.get_conditions()
