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
        Experiment.ObjectProperty("reference", self, value_type=Experiment)

        if(isinstance(ref,Experiment)):
            self.reference(ref)

    @classmethod
    def Condition(cls, cond, val):
        cls.DatatypeProperty.__init__(cond, self, **kwargs)
        self.cond(val)

