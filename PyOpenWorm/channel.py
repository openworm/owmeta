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
    channel_name : DatatypeProperty
        
    description : DatatypeProperty
        
    description_evidences : DatatypeProperty
        
    channel_type : DatatypeProperty
        
    channel_subtype : DatatypeProperty
        
    ion_type : DatatypeProperty
        
    ligand_type : DatatypeProperty
        
    gene_name : DatatypeProperty
        
    gene_WB_ID : DatatypeProperty
        
    gene_class : DatatypeProperty
        
    proteins : DatatypeProperty
        
    protein_sequence : DatatypeProperty
        
    uniprot_ID : DatatypeProperty
        
    pdb_ID : DatatypeProperty
        
    interpro_ID : DatatypeProperty
        
    structure : DatatypeProperty
        
    structure_image : DatatypeProperty
        
    expression_pattern : DatatypeProperty
        
    expression_evidences : DatatypeProperty
        
    """

    def __init__(self, subfamily=False, **kwargs):
        DataObject.__init__(self, **kwargs)
        # Get Models of this Channel
        Models(owner=self)
        Channel.DatatypeProperty('subfamily', owner=self)

        if isinstance(subfamily, basestring):
            self.subfamily = subfamily

#TODO: decide which of these parameters from CW we want to use in PyOW
#    channel_name 
#    description 
#    description_evidences 
#    channel_type 
#    channel_subtype 
#    ion_type 
#    ligand_type 
#    gene_name 
#    gene_WB_ID 
#    gene_class 
#    proteins 
#    protein_sequence 
#    uniprot_ID 
#    pdb_ID 
#    interpro_ID 
#    structure 
#    structure_image 
#    expression_pattern 
#    expression_evidences 
        
    def appearsIn(self):
        """
        TODO: Implement this method.
        Return a list of Cells that this ion channel appears in.
        """
        pass
