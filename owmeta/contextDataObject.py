from rdflib.term import URIRef
from .dataObject import DataObject, ObjectProperty, This
from .context import Context
from .context_common import CONTEXT_IMPORTS
from .mapper import mapped


@mapped
class ContextDataObject(DataObject):
    """ Represents a context """
    class_context = 'http://openworm.org/schema'
    rdf_type = URIRef('http://openworm.org/schema/Context')
    imports = ObjectProperty(value_type=This,
                             multiple=True,
                             link=CONTEXT_IMPORTS)
