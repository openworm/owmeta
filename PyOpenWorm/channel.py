from PyOpenWorm import *

class ChannelModel(dataObject):
    """
    A model for an ion channel.

    There may be multiple models for a single channel.

    Parameters
    ----------
    modelType : DatatypeProperty
        What this model is based on (either "homology" or "patch-clamp")
    
    Attributes
    ----------
    ion : DatatypeProperty
        The type of ion this channel selects for
    gating : DatatypeProperty
        The gating mechanism for this channel (either "voltage" or the name of a ligand)
    """

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
        list of ChannelModel
        """
        if len(self._models) > 0:
            for m in self._models:
                yield m
        # add something here to load() from db if _models is empty


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
    channelModel : Property
        Get experimental models of this ion channel
    """

    def __init__(self, name=False, **kwargs):
        DataObject.__init__(self, name=name, **kwargs)
        # Get experimental Models of this Channel
        ChannelModel(owner=self)
        Channel.DatatypeProperty('subfamily',owner=self)
