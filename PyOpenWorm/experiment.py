from PyOpenWorm import *

class Condition(Property):
    """
    Class for storing a condition of an experiment.
    Takes one value and stores it with a key.

    Parameters
    ----------
    condition : String
        Name of the condition (ex: "subject").
    value : any
        State of the condition for the experiment in question.
        Could be an object, string, integer; whatever is relevant.

    Attributes
    ----------
    condition : String
        Name of the condition (ex: "subject").
    value : any
        State of the condition for the experiment in question.
        Could be an object, string, integer; whatever is relevant.
    """
    multiple=True
    def __init__(self, *args, **kwargs):
        Property.__init__(self, 'condition', *args, **kwargs)
        self._conds = {}

    def get(self):
        #get conditions and values from the db
        if len(self._conds) > 0:
            for c in self._conds:
                yield c
        else:
            pass

    def set(self, condition, value):
        #add condition as datatype property to the experiment object
        Experiment.DatatypeProperty(condition, self)
        exec("self." + condition + "(value)" )
        #now add it to the _conds dictionary
        self._conds[condition] = value

class Experiment(DataObject):
    """
    Generic class for storing information about experiments

    Parameters
    ----------
    reference : Evidence
        Supporting article for this experiment.

    Attributes
    ----------
    condition : Property
        Experimental conditions, set by key.
    """

    def __init__(self, ref, **kwargs):
        DataObject.__init__(self, **kwargs)
        Experiment.ObjectProperty("reference", self, value_type=Evidence)

        if(isinstance(ref,Evidence)):
            self.reference(ref)

        Condition(owner=self)
