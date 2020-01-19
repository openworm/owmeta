from owmeta.mapper import mapped
from owmeta.dataObject import DataObject, DatatypeProperty


@mapped
class TDO(DataObject):
    rdf_type = 'http://openworm.org/entities/TDO'
    a = DatatypeProperty()
