import six
from PyOpenWorm.contextualize import contextualize_metaclass
from PyOpenWorm.context import Context, ContextMeta


class DocumentContextMeta(ContextMeta):

    def contextualize_class(self, context):
        return contextualize_metaclass(context, self)('Contextualized_' + self.__name__, (self,), dict())


class DocumentContext(six.with_metaclass(DocumentContextMeta, Context)):
    """ A Context that corresponds to a document. """

    def __new__(cls, *args, **kwargs):
        ores = super(DocumentContext, cls).__new__(cls)
        if cls.context is not None:
            res = ores.contextualize(cls.context)
            res.__init__ = type(ores).__init__.__get__(res, type(ores))
            type(ores).__init__(res, *args, **kwargs)
        else:
            res = ores
        return res

    def __init__(self, document):
        super(DocumentContext, self).__init__()
        self._document = document

    @property
    def identifier(self):
        return self._document.make_identifier(self._document.identifier.n3())

    @identifier.setter
    def identifier(self, v):
        pass
