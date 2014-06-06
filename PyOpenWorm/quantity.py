
class Quantity:
    @classmethod
    def parse(self, s):
        return Quantity(s, "units")

    def __init__(self, value, unit):
        self.value = value
        self.unit = unit
