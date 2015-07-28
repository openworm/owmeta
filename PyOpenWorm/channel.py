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
    A biological ion channel.

    Attributes
    ----------
    Models : Property
        Get experimental models of this ion channel
    channel_name : DatatypeProperty
        Ion channel's name
    description : DatatypeProperty
        A description of the ion channel
    gene_name : DatatypeProperty
        Name of the gene that codes for this ion channel
    gene_WB_ID : DatatypeProperty
        Wormbase ID of the encoding gene
    gene_class : DatatypeProperty
        Classification of the encoding gene
    proteins : DatatypeProperty
        Proteins associated with this channel
    expression_pattern : DatatypeProperty
       
    """

    def __init__(self, name=False, **kwargs):
        DataObject.__init__(self, **kwargs)
        # Get Models of this Channel
        Models(owner=self)

        Channel.DatatypeProperty('name', self) #channel_name
        Channel.DatatypeProperty('description',self) #description
        Channel.DatatypeProperty('gene_name', self) #gene_name
        Channel.DatatypeProperty('gene_WB_ID', self) #gene_WB_ID
        Channel.DatatypeProperty('expression_pattern', self) #expression_pattern
        Channel.DatatypeProperty('proteins', self, multiple=True) #proteins
        #TODO: assert this in the adapter instead
        #Channel.DatatypeProperty('description_evidences', self)
        #TODO: assert this in the adapter instead
        #Channel.DatatypeProperty('expression_evidences', self)

        if name:
            self.name(name)

    def appearsIn(self):
        """
        TODO: Implement this method.
        Return a list of Cells that this ion channel appears in.
        """
        pass

    def identifier(self, *args, **kwargs):
        # Copied from cell.py

        # If the DataObject identifier isn't variable, then self is a specific
        # object and this identifier should be returned. Otherwise, if our name
        # attribute is _already_ set, then we can get the identifier from it and
        # return that. Otherwise, there's no telling from here what our identifier
        # should be, so the variable identifier (from DataObject.identifier() must
        # be returned
        ident = DataObject.identifier(self, *args, **kwargs)
        if 'query' in kwargs and kwargs['query'] == True:
            if not DataObject._is_variable(ident):
                return ident

        if self.name.hasValue():
            # name is already set, so we can make an identifier from it
            n = next(self.name._get())
            return self.make_identifier(n)
        else:
            return ident

