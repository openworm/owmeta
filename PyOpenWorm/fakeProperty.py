class FakeProperty(object):

    def __init__(self, prop):
        self._p = prop
        self._p.owner_properties.append(self)

    @property
    def link(self):
        return self._p.link

    @property
    def linkName(self):
        return self._p.linkName

    @property
    def values(self):
        return (self._p,)

    def set(self, v):
        self._p.set(v)

    def unset(self, v):
        self._p.unset()

    def get(self):
        return self._p.get()

    @property
    def owner(self):
        return self._p.owner

    @property
    def multiple(self):
        return False

    @property
    def rdf(self):
        return self._p.rdf

    def __str__(self):
        return "FakeProperty(" + str(self._p.idl.n3()) + ")"
