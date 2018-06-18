from PyOpenWorm.dataObject import DataObject
from PyOpenWorm.evidence import Evidence


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

    Parameters
    ----------
    reference : Evidence
        Supporting article for this experiment.
    """
    class_context = 'http://openworm.org/schema/sci'

    def __init__(self, reference=None, **kwargs):
        super(Experiment, self).__init__(**kwargs)
        Experiment.ObjectProperty('reference',
                                  owner=self,
                                  value_type=Evidence,
                                  multiple=True)

        if isinstance(reference, Evidence):
            #TODO: make this so the reference asserts this Experiment when it is added
            self.reference(reference)

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


__yarom_mapped_classes__ = (Experiment,)
