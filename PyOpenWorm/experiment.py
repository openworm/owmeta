from PyOpenWorm import *


class Experiment(DataObject):
    """
    Generic class for storing information about experiments

    Parameters
    ----------
    reference : Evidence
        Supporting article for this experiment.
    """

    def __init__(self, reference=False, **kwargs):
        DataObject.__init__(self, **kwargs)
        Experiment.ObjectProperty('reference', owner=self, value_type=Evidence, multiple=True)

        if(isinstance(reference,Evidence)):
            #TODO: make this so the reference asserts this Experiment when it is added
            self.reference(reference)

        self._condits = {}

    def get_conditions(self):
        """Return conditions and their associated values in a dict."""
        for c in self.conditions:
            value = getattr(self, c)
            try:
                value()
                #property is callable
                self._condits[c] = value()
            except:
                if value:
                    #if property is not empty
                    self._condits[c] = value

        return self._condits

