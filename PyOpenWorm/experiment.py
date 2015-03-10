from PyOpenWorm import *

class Condition(DataObject):
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

    def __init__(self, condition=False, value=False, owner=False, **kwargs):
        DataObject.__init__(self, **kwargs)
        Condition.DatatypeProperty('condition', self)
        Condition.DatatypeProperty('value', self)
        Condition.DatatypeProperty('owner', self)

        if isinstance(condition, basestring):
            self.condition = condition

        if isinstance(value, basestring):
            self.value = value

        self.owner = owner

class Conditions(Property):
    """
    Used for storing and retrieving Conditions of an Experiment
    """
    multiple=True
    def __init__(self, *args, **kwargs):
        Property.__init__(self, 'conditions', *args, **kwargs)
        self._conds = []

    def get(self):
        """
        Get a list of Conditions for this Experiment.

        Parameters
        ----------
        None

        Returns
        -------
        set of Condition
        """
        if len(self._conds) > 0:
            for cond in self._conds:
                yield cond
        else:
            #load Condition objects with owner=self.owner
            c = Condition(owner=self.owner)
            for cond in c.load():
                self._conds.append(cond)
                yield cond

    def set(self, condition=False, value=False):
        #create new Conditon DataObject
        c = Condition(condition, value, self.owner)
        #add Condition key and value to _conds
        self._conds.append(c)

    def save(self):
        #overrides save
        for cond in self._conds:
            cond.save()


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

    def __init__(self, reference, **kwargs):
        DataObject.__init__(self, **kwargs)
        Experiment.ObjectProperty('reference', self, value_type=Evidence)

        if(isinstance(reference,Evidence)):
            self.reference(reference)

        Conditions(owner=self)
