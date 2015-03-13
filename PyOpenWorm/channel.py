from PyOpenWorm import *

class References(Property):
    multiple=True
    def __init__(self, **kwargs):
        Property.__init__(self, 'references', **kwargs)
        self._refs = []

    def set(self, e=False, **kwargs):
        """
        Add a reference to the list.
        This method will also take care of mapping the Evidence's assertion to
        this ChannelModel

        Parameters
        ----------
        e : Evidence or Experiment
            The Experiment or Evidence that supports this ChannelModel

        Returns
        -------
        None
        """
        if isinstance(e, Evidence):
            e.asserts(self.owner)
            self._refs.append(e)
        elif isinstance(e, Experiment):
            e = e.reference()
            e.asserts(self.owner)
            self._refs.append(e)

    def get(self, **kwargs):
        """
        Retrieve the reference list for this ChannelModel

        Parameters
        ----------
        None

        Returns
        -------
        Set of Evidence and Experiment objects
        """
        if len(self._refs) == 0:
            #Make dummy Evidence to load from db
            ev = Evidence()
            ev.asserts(self.owner)
            #Make dummy Experiment with this Evidence
            ex = Experiment(reference=ev)
            #load from db
            for e in ev.load():
                self._refs.append(e)
            for e in ex.load():
                self._refs.append(e)
        #now return the iterable set
        for r in self._refs:
            yield r

class ChannelModelType:
    patchClamp = "Patch clamp experiment"
    homologyEstimate = "Estimation based on homology"

class ChannelModel(DataObject):
    """
    A model for an ion channel.

    There may be multiple models for a single channel.

    Parameters
    ----------
    modelType : DatatypeProperty
        What this model is based on (either "homology" or "patch-clamp")

    Attributes
    ----------
    modelType : DatatypeProperty
        Passed in on construction
    ion : DatatypeProperty
        The type of ion this channel selects for
    gating : DatatypeProperty
        The gating mechanism for this channel ("voltage" or name of ligand(s) )
    references : Property
        Evidence for this model. May be either Experiment or Evidence object(s).
    conductance : DatatypeProperty
        The conductance of this ion channel. This is the initial value, and
        should be entered as a Quantity object.
    """

    def __init__(self, modelType=False, *args, **kwargs):
        DataObject.__init__(self, **kwargs)
        ChannelModel.DatatypeProperty('modelType', self)
        ChannelModel.DatatypeProperty('ion', self, multiple=True)
        ChannelModel.DatatypeProperty('gating', self, multiple=True)
        ChannelModel.DatatypeProperty('conductance', self)
        References(owner=self)

        #Change modelType value to something from ChannelModelType class on init
        if (isinstance(modelType, basestring)):
            modelType = modelType.lower()
            if modelType in ('homology', ChannelModelType.homologyEstimate):
                self.modelType(ChannelModelType.homologyEstimate)
            elif modelType in ('patch-clamp', ChannelModelType.patchClamp):
                self.modelType(ChannelModelType.patchClamp)

class Models(Property):
    multiple=True
    def __init__(self, **kwargs):
        Property.__init__(self, 'models', **kwargs)
        self._models = []

    def get(self, **kwargs):
        """
        Get a list of models for this channel

        Parameters
        ----------
        None

        Returns
        -------
        set of ChannelModel
        """

        if len(self._models) > 0:
            for m in self._models:
                yield m
        else:
            #make a dummy ChannelModel so we can load from db to memory
            c = ChannelModel()
            for m in c.load():
                self._models.append(m)
            #call `get()` again to yield ChannelModels the user asked for
            self.get()

    def set(self, m, **kwargs):
        """
        Add a model to this Channel

        Parameters
        ----------
        m : ChannelModel
            The model to be added (instance of ChannelModel class)

        Returns
        -------
        The ChannelModel being inserted (this is a side-effect)
        """

        self._models.append(m)
        return m

    def triples(self,**kwargs):
        for c in self._models:
            for x in c.triples(**kwargs):
                yield x

class Channel(DataObject):
    """
    An ion channel.

    Channels are identified by subtype name.

    Parameters
    ----------
    subfamily : string
        The subfamily to which the ion channel belongs

    Attributes
    ----------
    subfamily : DatatypeProperty
        The subfamily to which the ion channel belongs
    Models : Property
        Get experimental models of this ion channel
    """

    def __init__(self, subfamily=False, **kwargs):
        DataObject.__init__(self, **kwargs)
        # Get Models of this Channel
        Models(owner=self)
        Channel.DatatypeProperty('subfamily', owner=self)

        if isinstance(subfamily, basestring):
            self.subfamily = subfamily
