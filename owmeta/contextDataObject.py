from rdflib.term import URIRef
from .dataObject import DataObject, ObjectProperty, This
from .context import Context
from .context_common import CONTEXT_IMPORTS


class ContextDataObject(DataObject):
    """ Represents a context """
    class_context = 'http://openworm.org/schema'
    rdf_type = URIRef('http://openworm.org/schema/Context')
    imports = ObjectProperty(value_type=This,
                             multiple=True,
                             link=CONTEXT_IMPORTS)


__yarom_mapped_classes__ = (ContextDataObject,)
