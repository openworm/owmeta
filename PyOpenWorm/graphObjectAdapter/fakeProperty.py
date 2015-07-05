from yarom.yProperty import Property as P

class FakeProperty(P):

    def __init__(self, prop):
        self._p = prop

    @property
    def link(self):
        return self._p.link

    @property
    def values(self):
        return (self._p,)

    def set(self, v):
        self._p.set(v)

