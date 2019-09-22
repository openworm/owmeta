import unittest
from owmeta.channelworm import PatchClampExperiment, ChannelModel, ChannelModelType


class PatchClampExperimentTest(unittest.TestCase):

    def test_cw_init(self):
        PatchClampExperiment(cell='blah', delta_t=.002)


class ChannelModelTest(unittest.TestCase):

    def test_cm_init_pc_model_type(self):
        cm = ChannelModel(modelType='patch-clamp')
        self.assertEqual(ChannelModelType.patchClamp, cm.modelType.onedef())

    def test_cm_init_homology_model_type(self):
        cm = ChannelModel(modelType='homology')
        self.assertEqual(ChannelModelType.homologyEstimate, cm.modelType.onedef())

    def test_cm_init_unknown_model_type(self):
        cm = ChannelModel(modelType='homolog')
        self.assertIsNone(cm.modelType.onedef())

    def test_cm_init_homoly_model_type(self):
        cm = ChannelModel(modelType=23)
        self.assertIsNone(cm.modelType.onedef())
