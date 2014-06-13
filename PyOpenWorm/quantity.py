import pint as Q

class Quantity:
    ur = Q.UnitRegistry()
    @classmethod
    def parse(self, s):
        q = self.ur.Quantity(s)
        my_q = Quantity(0,"mL")
        my_q._quant = q
        return my_q

    def __init__(self, value, unit):
        self._quant = self.ur.Quantity(value,unit)

    @property
    def unit(self):
        return str(self._quant.units)

    @property
    def value(self):
        return self._quant.magnitude

