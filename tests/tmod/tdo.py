from owmeta_core.mapper import mapped
from owmeta_core.dataobject import DataObject, DatatypeProperty


@mapped
class TDO(DataObject):
    rdf_type = 'http://openworm.org/entities/TDO'
    a = DatatypeProperty()
