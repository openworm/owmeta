from .mapper import mapped
from .dataObject import DataObject


@mapped
class BiologyType(DataObject):
    class_context = 'http://openworm.org/schema/bio'
