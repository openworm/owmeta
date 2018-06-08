from PyOpenWorm.dataObject import DataObject, ObjectProperty, This


class ContextDataObject(DataObject):
    """ Represents a context """
    class_context = 'http://openworm.org/schema'
    imports = ObjectProperty(value_type=This,
                             multiple=True)


__yarom_mapped_classes__ = (ContextDataObject,)
