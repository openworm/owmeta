from owmeta_core.dataobject import DataObject, ObjectProperty

from . import SCI_CTX
from .document import Document


class Experiment(DataObject):
    """
    Generic class for storing information about experiments

    Should be overridden by specific types of experiments
    (example: see PatchClampExperiment in channelworm.py).

    Overriding classes should have a list called "conditions" that
    contains the names of experimental conditions for that particular
    type of experiment.
    Each of the items in "conditions" should also be either a
    DatatypeProperty or ObjectProperty for the experiment as well.
    """

    class_context = SCI_CTX

    reference = ObjectProperty(value_type=Document, multiple=True)
    ''' Supporting article for this experiment. '''

    def __init__(self, **kwargs):
        super(Experiment, self).__init__(**kwargs)
        self._condits = {}

    def get_conditions(self):
        """Return conditions and their associated values in a dict."""
        if not hasattr(self, 'conditions'):
            raise NotImplementedError('"conditions" attribute must be overridden')

        for c in self.conditions:
            value = getattr(self, c)
            if callable(value):
                self._condits[c] = value()
            else:
                if value:
                    #if property is not empty
                    self._condits[c] = value

        return self._condits
