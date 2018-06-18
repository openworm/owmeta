from __future__ import absolute_import
from PyOpenWorm.pProperty import Property
from .DataTestTemplate import _DataTest


class PropertyTest(_DataTest):
    def test_one(self):
        """ `one` should return None if there isn't a value or just the value if there is one """
        class T(Property):
            def __init__(self):
                Property.__init__(self)
                self.b = False

            def get(self):
                if self.b:
                    yield "12"
        t = T()
        self.assertIsNone(t.one())
        t.b=True
        self.assertEqual('12', t.one())
