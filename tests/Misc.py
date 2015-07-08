import PyOpenWorm as P
import unittest

class Misc(unittest.TestCase):
    """Miscellaneous tests that have cropped up"""
    def test_generators_do_not_reset(self):
        """
        This is for issue #175.  For some reason,
        the generators were being reset when called,
        meaning that the second call to len(list(neurons))
        below returned 0.
        """

        net = P.Worm().neuron_network()
        neurons = net.neurons()
        check1 = len(list(neurons))
        check2 = len(list(neurons))
        self.assertEqual(check1, check2)
