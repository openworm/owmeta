from owmeta_core.mapper import mapped
from owmeta_core.dataobject import DataObject


@mapped
class BiologyType(DataObject):
    class_context = 'http://openworm.org/schema/bio'
