import rdflib as R

from PyOpenWorm.channelworm import ChannelModel
from PyOpenWorm.biology import BiologyType


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
        from PyOpenWorm.cell import Cell
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
                               value_type=Cell)
        self.model = Channel.ObjectProperty(value_type=ChannelModel)
        # TODO: assert this in the adapter instead
        # Channel.DatatypeProperty('description_evidences', self)
        # TODO: assert this in the adapter instead
        # Channel.DatatypeProperty('expression_evidences', self)

        if name:
            self.name(name)

    @property
    def defined(self):
        return super(Channel, self).defined or self.name.has_defined_value()

    @property
    def identifier(self):
        if super(Channel, self).defined:
            return super(Channel, self).identifier
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

    @property
    def identifier(self):
        if super(ExpressionPattern, self).defined:
            return super(ExpressionPattern, self).identifier
        else:
            return self.make_identifier(self.wormbaseID.defined_values[0])


__yarom_mapped_classes__ = (Channel, ExpressionPattern)
