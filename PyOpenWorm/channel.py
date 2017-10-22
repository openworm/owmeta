import rdflib as R
from .pProperty import Property
import PyOpenWorm
from yarom import yarom_import

ChannelModel = yarom_import('PyOpenWorm.channelworm.ChannelModel')
BiologyType = yarom_import('PyOpenWorm.biology.BiologyType')


# XXX: Why is this not an ObjectProperty?
class Models(Property):
    multiple = True

    def __init__(self, **kwargs):
        super(Models, self).__init__('models', **kwargs)
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
            # make a dummy ChannelModel so we can load from db to memory
            c = ChannelModel()
            for m in c.load():
                self._models.append(m)
            # call `get()` again to yield ChannelModels the user asked for
            if len(self._models) > 0:
                self.get()

    @property
    def values(self):
        return self._models

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

    def triples(self, **kwargs):
        for c in self._models:
            for x in c.triples(**kwargs):
                yield x


class Channel(BiologyType):
    """
    A biological ion channel.

    Attributes
    ----------
    Models : Property
        Get experimental models of this ion channel
    subfamily : DatatypeProperty
        Ion channel's subfamily
    name : DatatypeProperty
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
    expression_pattern : ObjectProperty

    """

    class_context = BiologyType.class_context

    def __init__(self, name=False, **kwargs):
        super(Channel, self).__init__(**kwargs)
        # Get Models of this Channel
        Models(owner=self)
        Channel.DatatypeProperty('subfamily', owner=self)
        Channel.DatatypeProperty('description', owner=self)
        Channel.DatatypeProperty('name', self)
        Channel.DatatypeProperty('description', self)
        Channel.DatatypeProperty('gene_name', self)
        Channel.DatatypeProperty('gene_WB_ID', self)
        Channel.ObjectProperty('expression_pattern',
                               owner=self,
                               multiple=True,
                               value_type=ExpressionPattern)
        Channel.DatatypeProperty('neuroML_file', owner=self)
        Channel.DatatypeProperty('proteins', self, multiple=True)
        Channel.ObjectProperty('appearsIn', self, multiple=True,
                               value_type=PyOpenWorm.cell.Cell)
        # TODO: assert this in the adapter instead
        # Channel.DatatypeProperty('description_evidences', self)
        # TODO: assert this in the adapter instead
        # Channel.DatatypeProperty('expression_evidences', self)

        if name:
            self.name(name)

    @property
    def defined(self):
        return super(Channel, self).defined or self.name.has_defined_value()

    def identifier(self):
        if super(Channel, self).defined:
            return super(Channel, self).identifier()
        else:
            # name is already set, so we can make an identifier from it
            return self.make_identifier(self.name.defined_values[0])


class ExpressionPattern(BiologyType):

    class_context = BiologyType.class_context

    def __init__(self, wormbaseID=None, description=None, **kwargs):
        super(ExpressionPattern, self).__init__(**kwargs)
        ExpressionPattern.DatatypeProperty('wormbaseID', owner=self)
        ExpressionPattern.DatatypeProperty('wormbaseURL', owner=self)
        ExpressionPattern.DatatypeProperty('description', owner=self)

        if wormbaseID:
            self.wormbaseID(wormbaseID)
            self.wormbaseURL(R.URIRef("http://www.wormbase.org/species/all/expr_pattern/"+wormbaseID))

        if description:
            self.description(description)

    @property
    def defined(self):
        return super(ExpressionPattern, self).defined \
                or self.wormbaseID.has_defined_value()

    def identifier(self):
        if super(ExpressionPattern, self).defined:
            return super(ExpressionPattern, self).identifier()
        else:
            return self.make_identifier(self.wormbaseID.defined_values[0])
