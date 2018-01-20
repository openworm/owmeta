import wrapt


class Contextualizable(object):
    __slots__ = ()

    @property
    def context(self):
        return None

    def contextualize(self, context):
        return self


UNSET = object()


def contextualize_metaclass(context, self):
    outer_self = self

    class _H(type(self)):
        def __init__(self, name, bases, dct):
            super(_H, self).__init__(name, bases, dct)
            self.__ctx = context
            if self.__ctx is None:
                raise Exception(name)

        def __call__(self, *args, **kwargs):
            if self.__ctx is None:
                raise Exception()
            return super(_H, self).__call__(*args, **kwargs)

        def __repr__(self):
            return repr(outer_self) + '.contextualize_class(' + repr(context) + ')'

        @property
        def context(self):
            return self.__ctx

    return _H


class ContextualizingProxy(wrapt.ObjectProxy):
    def __init__(self, ctx, *args, **kwargs):
        super(ContextualizingProxy, self).__init__(*args, **kwargs)
        self._self_context = ctx

    def __getattribute__(self, name):
        """ This behavior is what I would expect, but wrapt doesn't work this way..."""
        if name is 'context':
            return self._self_context

        if name not in ('__wrapped__', '__factory__', '__class__'):
            k = UNSET
            if name in type(self).__dict__:
                k = type(self).__dict__[name]
            else:
                for t in type(self.__wrapped__).mro():
                    if name in t.__dict__:
                        k = t.__dict__[name]
                        break

            if k is not UNSET:
                if hasattr(k, '__get__'):
                    # Classmethods are special-cased. We mostly don't do
                    # anything to the class of a proxied object, and we want
                    # classmethods to 'just work', so for this case, we pass in
                    # the wrapped's type
                    if isinstance(k, classmethod):
                        return k.__get__(self.__wrapped__, type(self.__wrapped__))
                    else:
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
