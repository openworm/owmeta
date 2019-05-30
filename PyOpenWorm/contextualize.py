from __future__ import print_function
import wrapt
from weakref import WeakValueDictionary


class BaseContextualizable(object):

    def __init__(self, *args, **kwargs):
        super(BaseContextualizable, self).__init__(*args, **kwargs)

        if not hasattr(self, '_contexts'):
            self._contexts = WeakValueDictionary()

    @property
    def context(self):
        return None

    def contextualize(self, context):
        """
        Return an object with the given context. If the provided ``context`` is
        `None`, then `self` MUST be returned unmodified.

        It is generally not correct to set a field on the object and return the
        same object as this would change the context for other users of the
        object. Also, returning a copy of the object is usually inappropriate
        for mutable objects. Immutable objects may maintain a 'context'
        property and return a copy of themselves with that property set to the
        provided ``context`` argument.
        """
        ctxd = self._contexts.get(context)
        if ctxd is not None:
            return ctxd
        ctxd = self.contextualize_augment(context)
        self._contexts[context] = ctxd
        return ctxd

    def decontextualize(self):
        """
        Return the object with all contexts removed
        """
        return self

    def add_contextualization(self, context, contextualization):
        try:
            self._contexts[context] = contextualization
        except AttributeError:
            self._contexts = WeakValueDictionary()
            self._contexts[context] = contextualization

    def contextualize_augment(self, context):
        return self


class Contextualizable(BaseContextualizable):
    """
    A BaseContextualizable with the addition of a default behavior of setting
    the context from the class's 'context' attribute. This generally requires
    that for the metaclass of the Contextualizable that a 'context' data
    property is defined. For example:

    >>> class AMeta(ContextualizableClass):
    >>>     @property
    >>>     def context(self):
    >>>         return self.__context

    >>>     @context.setter
    >>>     def context(self, ctx):
    >>>         self.__context = ctx

    >>> class A(six.with_metaclass(Contextualizable)):
    >>>     pass

    """

    def __new__(cls, *args, **kwargs):
        """
        This is defined so that the __init__ method gets a contextualized
        instance, allowing for statements made in __init__ to be contextualized.
        """
        ores = super(Contextualizable, cls).__new__(cls)
        # XXX: This shouldn't really ever be the property...
        if not isinstance(cls.context, property):
            ores.context = cls.context
            ores._contexts = WeakValueDictionary()
            ores.add_contextualization(cls.context, ores)
            res = ores
        else:
            ores.context = None
            res = ores

        return res

    @property
    def context(self):
        return self.__context

    @context.setter
    def context(self, ctx):
        if isinstance(ctx, property):
            raise Exception('An attempt was made to set a property as the context. This is likely unintended')
        self.__context = ctx


UNSET = object()


def contextualize_metaclass(context, self):

    class _H(type(self)):
        def __init__(self, name, bases, dct):
            super(_H, self).__init__(name, bases, dct)
            self.__ctx = context

        def __repr__(self):
            return self.__name__ + '.contextualize_class(' + repr(context) + ')'

        @property
        def context(self):
            return self.__ctx
    # Setting the name just for debugging...don't care much about the other
    # attributes for now.
    _H.__name__ = 'Ctxd_Meta_' + self.__name__

    return _H


def get_wrapped(self):
    return super(ContextualizingProxy, self).__getattribute__('__wrapped__')


class ContextualizingProxy(wrapt.ObjectProxy):
    __slots__ = ('_self_context', '_self_overrides')

    def __init__(self, ctx, *args, **kwargs):
        super(ContextualizingProxy, self).__init__(*args, **kwargs)
        self._self_context = ctx
        self._self_overrides = dict()

    def add_attr_override(self, name, override):
        self._self_overrides[name] = override

    def __getattribute__(self, name):
        # This behavior is what I would expect, but wrapt doesn't work this way...
        # General note: This method should never call itself directly although
        # it may call itself indirectly through a descriptor. Use
        # object.__getattribute__ or super(ContextualizingProxy, self).__getattribute__
        # as appropriate for attribute accesses from within
        if name == 'context':
            return super(ContextualizingProxy, self).__getattribute__('_self_context')

        override = super(ContextualizingProxy, self).__getattribute__('_self_overrides').get(name, None)
        if override is not None:
            return override
        wrapped = None
        if name not in ('__wrapped__', '__factory__', '__class__'):
            k = UNSET
            if name in type(self).__dict__:
                k = type(self).__dict__[name]
            else:
                wrapped = get_wrapped(self)
                for t in type(wrapped).mro():
                    if name in t.__dict__:
                        k = t.__dict__[name]
                        break

            if k is not UNSET:
                if hasattr(k, '__get__'):
                    if not hasattr(k, '__set__'):
                        # We have to check the __wrapped__. Don't check our
                        # self since all we have is a context.
                        try:
                            return k.__get__(self, type(self))
                        except AttributeError:
                            # The __wrapped__ doesn't have the named attribute
                            # Pass in this proxy to the descriptor so that
                            # methods, etc.  can access their context

                            # Classmethods are special-cased. We mostly don't do
                            # anything to the class of a proxied object, and we want
                            # classmethods to 'just work', so for this case, we pass in
                            # the wrapped's type
                            if isinstance(k, classmethod):
                                wrapped = get_wrapped(self) if wrapped is None else wrapped
                                return k.__get__(wrapped, type(wrapped))
                            else:
                                raise
                    # it's a data descriptor
                    elif isinstance(k, classmethod):
                        wrapped = get_wrapped(self) if wrapped is None else wrapped
                        return k.__get__(wrapped, type(wrapped))
                    else:
                        return k.__get__(self, type(self))
                else:
                    try:
                        wrapped = get_wrapped(self) if wrapped is None else wrapped
                        return object.__getattribute__(wrapped, name)
                    except AttributeError:
                        return k

        return super(ContextualizingProxy, self).__getattribute__(name)

    def __setattr__(self, name, value):
        # This was copied from wrapt/wrappers.py with the addition noted below
        if name.startswith('_self_'):
            object.__setattr__(self, name, value)
        elif name == '__wrapped__':
            raise AttributeError('Cannot set wrapped after initialization')
        elif name == '__qualname__':
            setattr(get_wrapped(self), name, value)
            object.__setattr__(self, name, value)
        else:
            # Added compared to wrapt.
            mro = type(self).mro()
            for x in mro:
                attr = x.__dict__.get(x, None)
                if hasattr(attr, '__set__'):
                    attr.__set__(self, value)
                    break
            else: # no break
                setattr(get_wrapped(self), name, value)

    def __call__(self, *args, **kwargs):
        # Omitted by default and only included in CallableObjectProxy by wrapt.
        # Dunno why.
        return get_wrapped(self).__call__.__func__(self, *args, **kwargs)

    def __repr__(self):
        return 'ContextualizingProxy({}, {})'.format(repr(self._self_context),
                                                     repr(self.__wrapped__))


class ContextualizableClass(type):
    """ A super-type for contextualizable classes """

    def __new__(self, name, typ, dct):
        res = super(ContextualizableClass, self).__new__(self, name, typ, dct)
        res.__contexts = WeakValueDictionary()
        return res

    def __getattribute__(self, name):
        # This method is optimized to save a comparison in the common case
        if name in ('contextualize', 'contextualize_augment'):
            if name == 'contextualize_augment':
                name = 'contextualize_class_augment'
            else:
                name = 'contextualize_class'
        return super(ContextualizableClass, self).__getattribute__(name)

    def contextualize_class(self, context):
        ctxd = self.__contexts.get(context)
        if ctxd is not None:
            return ctxd
        ctxd = self.contextualize_class_augment(context)
        self.__contexts[context] = ctxd
        return ctxd

    def contextualize_class_augment(self, context, **kwargs):
        if context is None:
            return self
        _H = contextualize_metaclass(context, self)
        res = _H(self.__name__, (self,), dict(class_context=context.identifier, **kwargs))
        res.__module__ = self.__module__
        return res


def contextualized_new(ccls):
    def _helper(cls, *args, **kwargs):
        ores = super(ccls, cls).__new__(cls)
        if cls.context is not None:
            res = ores.contextualize(cls.context)
            res.__init__ = type(ores).__init__.__get__(res, type(ores))
            type(ores).__init__(res, *args, **kwargs)
        else:
            res = ores
        return res
    return _helper


class _ContextualzingProxyMetaType(type(ContextualizingProxy)):
    def __new__(self, name, typ, dct, oclasstyp):
        res = super(_ContextualzingProxyMetaType, self).__new__(self, name, typ, dct)
        res._oct = oclasstyp
        res.__module__ = oclasstyp.__module__
        return res

    def __init__(self, name, typ, dct, oclasstyp):
        self._oct = oclasstyp

    def __getattr__(self, name):
        try:
            return super(_ContextualzingProxyMetaType, self).__getattr__(name)
        except AttributeError:
            return getattr(self._oct, name)


def decontextualize_helper(obj):
    """
    Removes contexts from a ContextualizingProxy
    """
    ret = obj
    while isinstance(ret, ContextualizingProxy):
        ret = get_wrapped(ret)
    return contextualize_helper(None, ret, True)


def contextualize_helper(context, obj, noneok=False):
    """
    Does some extra stuff to make access to the type of a ContextualizingProxy
    work more-or-less like access to the the wrapped object
    """
    if not noneok and context is None:
        return obj

    ctx = getattr(obj, 'context', None)
    if ctx is not None and ctx is context:
        return obj

    # Copy our special properties into the class so that they
    # always take precedence over attributes of the same name added
    # during construction of a derived class. This is to save
    # duplicating the implementation for them in all derived classes.

    pclass_dct = dict()
    for k, v in vars(obj.__class__).items():
        if k not in ('__wrapped__', '__name__', '__doc__',
                     '__module__', '__weakref__', '__dict__',
                     '__init__'):
            if hasattr(v, '__get__'):
                pclass_dct[k] = v
            else:
                pclass_dct[k] = proxy_to_X(obj.__class__, k)

    newtyp = _ContextualzingProxyMetaType('CtxProxyClass_' + obj.__class__.__name__,
                                          (ContextualizingProxy,),
                                          pclass_dct,
                                          type(obj.__class__))
    res = newtyp(context, obj)
    obj._contexts[context] = res
    return res


class proxy_to_X(object):
    __slots__ = ('_oclass', '_key')

    def __init__(self, oclass, key):
        self._oclass = oclass
        self._key = key

    def __get__(self, o, typ):
        if o is None:
            return getattr(self._oclass, self._key)
        else:
            raise AttributeError()

    def __str__(self):
        return 'proxy_to_' + self._key

    def __repr__(self):
        return 'contextualize.proxy_to_X({}, {})'.format(repr(self._oclass), repr(self._key))
