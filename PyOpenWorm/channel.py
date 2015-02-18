from PyOpenWorm import *

class ChannelModel(Property):
    multiple=True
    def __init__(self, **kwargs):
        Property.__init__(self, 'channelModel', **kwargs)
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
