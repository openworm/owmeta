from owmeta.dataObject import DataObject, DatatypeProperty


class TDO(DataObject):
    rdf_type = 'http://openworm.org/entities/TDO'
    a = DatatypeProperty()


__yarom_mapped_classes__ = (TDO,)
