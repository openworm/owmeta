from PyOpenWorm import *

class Conditions(Property):
    def __init__(self, **kwargs):
        Property.__init__(self, 'conditions', **kwargs)
        self._conds = {}

    def get(self, **kwargs):
        """
        Get the conditions of an experiment object.

        Returns
        -------
        Python dict of experimental conditions.
        """

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
        # Get conditions associated with this experiment
        Conditions(owner=self)

        if(isinstance(ref,Experiment)):
            self.reference(ref)
