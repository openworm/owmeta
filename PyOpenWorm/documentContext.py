import six
from PyOpenWorm.contextualize import contextualize_metaclass, contextualized_new
from PyOpenWorm.context import Context, ContextMeta


class DocumentContextMeta(ContextMeta):

    def contextualize_class(self, context):
        if context is None:
            return self
        return contextualize_metaclass(context, self)('_H2', (self,), dict())


class DocumentContext(six.with_metaclass(DocumentContextMeta, Context)):
    """ A Context that corresponds to a document. """

    def __init__(self, document):
        super(DocumentContext, self).__init__()
        self._document = document

    @property
    def identifier(self):
        return self._document.make_identifier(self._document.identifier.n3())

    @identifier.setter
    def identifier(self, v):
        pass


DocumentContext.__new__ = contextualized_new(DocumentContext)
