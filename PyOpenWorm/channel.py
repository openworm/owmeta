from PyOpenWorm import *

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

