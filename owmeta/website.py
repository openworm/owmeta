from rdflib.term import URIRef

from owmeta_core.dataobject import DatatypeProperty

from . import SCI_CTX
from .document import BaseDocument


class Website(BaseDocument):
    """ A representation of a website """

    class_context = SCI_CTX

    url = DatatypeProperty()
    ''' A URL for the website '''

    title = DatatypeProperty()
    ''' The official name for the website '''

    def __init__(self, title=None, **kwargs):
        super(Website, self).__init__(rdfs_comment=title, title=title, **kwargs)

    def defined_augment(self):
        return self.url.has_defined_value()

    def identifier_augment(self):
        return URIRef(self.url.defined_values[0].identifier)
