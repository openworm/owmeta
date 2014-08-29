
class Quantity:
    # Unit registry

    _ur = None
    @classmethod
    def ur(cls):
        import pint as Q
        if cls._ur is None:
            cls._ur = Q.UnitRegistry()

        return cls._ur

    @classmethod
    def parse(self, s):
        q = self.ur().Quantity(s)
        my_q = Quantity(0,"mL")
        my_q._quant = q
        return my_q

    def __init__(self, value, unit):
        # XXX: Pint adds about a second to the import
        #      time. Hiding it away in here makes
        #      everything better.
        self._quant = self.ur().Quantity(value,unit)

    @property
    def unit(self):
        return str(self._quant.units)

    @property
    def value(self):
        return self._quant.magnitude

