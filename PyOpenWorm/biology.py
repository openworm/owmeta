from yarom import yarom_import

DataObject = yarom_import('PyOpenWorm.dataObject.DataObject')


class BiologyType(DataObject):
    class_context = 'http://openworm.org/schema/bio'
