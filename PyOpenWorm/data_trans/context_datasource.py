from ..context import Context
from ..contextDataObject import ContextDataObject
from rdflib.term import URIRef
from rdflib.namespace import Namespace


class VariableIdentifierMixin(object):
    def __init__(self, maker=None, **kwargs):
        if maker is not None:
            conf = kwargs.pop('conf', maker.conf)
            super(VariableIdentifierMixin, self).__init__(conf=conf, **kwargs)
        else:
            super(VariableIdentifierMixin, self).__init__(**kwargs)
        self.maker = maker

    @property
    def identifier(self):
        return self.identifier_helper()

    @identifier.setter
    def identifier(self, a):
        pass

    def identifier_helper(self):
        if self.maker is not None:
            return self.maker.identifier
        else:
            return super(VariableIdentifierMixin, self).identifier


class VariableIdentifierContext(VariableIdentifierMixin, Context):
    '''
    A Context that gets its identifier and its configuration from its 'maker'
    passed in at initialization
    '''

    @property
    def rdf_object(self):
        if self._rdf_object is None:
            self._rdf_object = VariableIdentifierContextDataObject.contextualize(self.context)(maker=self)

        return self._rdf_object.contextualize(self.context)


class VariableIdentifierContextDataObject(VariableIdentifierMixin, ContextDataObject):
    '''
    A ContextDataObject that gets its identifier and its configuration from its 'maker' passed in at initialization
    '''

    rdf_type = URIRef('http://openworm.org/schema/Context#variable')
    rdf_namespace = Namespace(rdf_type + '#')

    def defined_augment(self):
        return self.maker is not None and self.maker.identifier is not None


__yarom_mapped_classes__ = (VariableIdentifierContextDataObject,)
