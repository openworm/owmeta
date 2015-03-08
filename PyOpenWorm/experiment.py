from PyOpenWorm import *

class Experiment(DataObject):
    """
    Generic class for storing information about experiments

    Parameters
    ----------
    reference : Evidence
        Supporting article for this experiment.

    Attributes
    ----------
    conditions : Property
        Experimental conditions, set by key.
    """

    def __init__(self, ref, **kwargs):
        DataObject.__init__(self, **kwargs)
        Experiment.ObjectProperty("reference", self, value_type=Evidence)

        if(isinstance(ref,Evidence)):
            self.reference(ref)

    def Condition(self, cond, val):
        Experiment.DatatypeProperty(cond, self)
        exec("self." + cond + "(val)" )
