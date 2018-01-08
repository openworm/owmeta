import wrapt


class Contextualizable(object):
    __slots__ = ()

    @property
    def context(self):
        return None

    def contextualize(self, context):
        return self


UNSET = object()


class ContextualizingProxy(wrapt.ObjectProxy):
    def __init__(self, ctx, *args, **kwargs):
        super(ContextualizingProxy, self).__init__(*args, **kwargs)
        self._self_context = ctx

    @property
    def context(self):
        return self._self_context

    def __getattribute__(self, name):
        """ This behavior is what I would expect, but wrapt doesn't work that way..."""
        if name not in ('__wrapped__', '__factory__', '__class__'):
            k = UNSET
            if name in type(self).__dict__:
                k = type(self).__dict__[name]
            elif name in type(self.__wrapped__).__dict__:
                k = type(self.__wrapped__).__dict__[name]

            if k is not UNSET:
                if hasattr(k, '__get__'):
                    return k.__get__(self, type(self))
                else:
                    return k

        return super(ContextualizingProxy, self).__getattribute__(name)

    def __call__(self, *args, **kwargs):
        return self.__wrapped__(*args, **kwargs)

    def __repr__(self):
        return 'ContextualizingProxy({}, {})'.format(repr(self._self_context),
                                                     repr(self.__wrapped__))


class ContextualizableClass(type):
    """ A super-type for contextualizable classes """

    def __getattribute__(self, name):
        if name != 'contextualize':
            return super(ContextualizableClass, self).__getattribute__(name)
        else:
            return super(ContextualizableClass, self).__getattribute__('contextualize_class')

    def contextualize_class(self, context):
        return self
