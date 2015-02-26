from PyOpenWorm import *

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
        The gating mechanism for this channel (either "voltage" or the name of a ligand)
    """

    def __init__(self, modelType, *args, **kwargs):
        DataObject.__init__(self, **kwargs)
        ChannelModel.DatatypeProperty("modelType", self)
        ChannelModel.DatatypeProperty("ion", self, multiple=True)
        ChannelModel.DatatypeProperty("gating", self, multiple=True)

    #Change modelType value to something from ChannelModelType class
    if (isinstance(modelType, basestring)):
        modelType = modelType.lower()
        if modelType in ('homology', ChannelModelType.homologyEstimate):
            self.modelType(ChannelModelType.homologyEstimate)
        elif modelType in ('patch-clamp', ChannelModelType.patchClamp):
            self.modelType(ChannelModelType.patchClamp)

class Model(Property):
    multiple=True
    def __init__(self, **kwargs):
        Property.__init__(self, 'model', **kwargs)
        self._models = []
    
    def get(self, **kwargs):
        """
        Get a list of models for this channel

        Parameters
        ----------
        None

        Returns
        -------
        list of ChannelModel
        """

        if len(self._models) > 0:
            for m in self._models:
                yield m
        # add something here to load() from db if _models is empty

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
    name : DatatypeProperty
        The subfamily to which the ion channel belongs
    Model : Property
        Get experimental models of this ion channel
    """

    def __init__(self, name=False, **kwargs):
        DataObject.__init__(self, name=name, **kwargs)
        # Get Models of this Channel
        Model(owner=self)
        Channel.DatatypeProperty('subfamily',owner=self)
