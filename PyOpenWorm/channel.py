import rdflib as R

from .dataObject import DatatypeProperty, ObjectProperty
from .channelworm import ChannelModel
from .biology import BiologyType
from .channel_common import CHANNEL_RDF_TYPE
from .cell_common import CELL_RDF_TYPE


class ExpressionPattern(BiologyType):

    class_context = BiologyType.class_context

    wormbaseid = DatatypeProperty()
    wormbaseURL = DatatypeProperty()
    description = DatatypeProperty()

    def __init__(self, wormbaseid=None, description=None, **kwargs):
        super(ExpressionPattern, self).__init__(**kwargs)

        if wormbaseid:
            self.wormbaseid(wormbaseid)
            self.wormbaseURL(R.URIRef("http://www.wormbase.org/species/all/expr_pattern/" + wormbaseid))

    @property
    def defined(self):
        return super(ExpressionPattern, self).defined \
                or self.wormbaseid.has_defined_value()

    @property
    def identifier(self):
        if super(ExpressionPattern, self).defined:
            return super(ExpressionPattern, self).identifier
        else:
            return self.make_identifier(self.wormbaseid.defined_values[0])


class Channel(BiologyType):
    """
    A biological ion channel.

    Attributes
    ----------
    Models : Property
    """

    class_context = BiologyType.class_context
    rdf_type = CHANNEL_RDF_TYPE

    subfamily = DatatypeProperty()
    ''' Ion channel's subfamily '''

    name = DatatypeProperty()
    ''' Ion channel's name '''

    description = DatatypeProperty()
    ''' A description of the ion channel '''

    gene_name = DatatypeProperty()
    ''' Name of the gene that codes for this ion channel '''

    gene_class = DatatypeProperty()
    ''' Classification of the encoding gene '''

    gene_WB_ID = DatatypeProperty()
    ''' Wormbase ID of the encoding gene '''

    expression_pattern = ObjectProperty(multiple=True,
                                        value_type=ExpressionPattern)
    ''' A pattern of expression of this cell within an organism '''

    neuroml_file = DatatypeProperty()
    ''' A NeuroML describing a model of this ion channel '''

    proteins = DatatypeProperty(multiple=True)
    ''' Proteins associated with this channel '''

    appearsIn = ObjectProperty(multiple=True, value_rdf_type=CELL_RDF_TYPE)
    ''' Cell types in which the ion channel has been expressed '''

    model = ObjectProperty(value_type=ChannelModel)
    ''' Get experimental models of this ion channel '''

    def __init__(self, name=None, **kwargs):
        super(Channel, self).__init__(name=name, **kwargs)

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


__yarom_mapped_classes__ = (Channel, ExpressionPattern)
