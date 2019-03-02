from ..context import Context
from ..contextDataObject import ContextDataObject


class VariableIdentifierMixin(object):
    def __init__(self, maker, **kwargs):
        conf = kwargs.pop('conf', maker.conf)
        super(VariableIdentifierMixin, self).__init__(conf=conf, **kwargs)
        self.maker = maker

    @property
    def identifier(self):
        return self.identifier_helper()

    @identifier.setter
    def identifier(self, a):
        pass

    def identifier_helper(self):
        return self.maker.identifier


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

    def defined_augment(self):
        return self.maker.identifier is not None
