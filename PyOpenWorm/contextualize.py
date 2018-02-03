import wrapt


class Contextualizable(object):
    __slots__ = ()

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
        return self


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

    return _H


def get_wrapped(self):
    return super(ContextualizingProxy, self).__getattribute__('__wrapped__')


class ContextualizingProxy(wrapt.ObjectProxy):
    def __init__(self, ctx, *args, **kwargs):
        super(ContextualizingProxy, self).__init__(*args, **kwargs)
        self._self_context = ctx
        self._self_overrides = dict()

    def add_attr_override(self, name, override):
        self._self_overrides[name] = override

    def __getattribute__(self, name):
        """ This behavior is what I would expect, but wrapt doesn't work this way..."""
        if name is 'context':
            return super(ContextualizingProxy, self).__getattribute__('_self_context')

        override = super(ContextualizingProxy, self).__getattribute__('_self_overrides').get(name, None)
        if override is not None:
            return override
        # debug = False
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
                        # if debug: print('not a data descriptor...')
                        # We have to check the __wrapped__. Don't check our
                        # self since all we have is a context.
                        try:
                            # if debug: print('getting attribute on
                            # wrapped...', type(self.__wrapped__),
                            # id(self.__wrapped__))
                            wrapped = get_wrapped(self) if wrapped is None else wrapped
                            res = object.__getattr__(wrapped, name)
                            # if debug: print('got attribute on wrapped', res)
                            return res
                        except AttributeError:
                            # The __wrapped__ doesn't have the named attribute
                            # Pass in this proxy to the descriptor so that
                            # methods, etc.  can access their context
                            #
                            # Classmethods are special-cased. We mostly don't do
                            # anything to the class of a proxied object, and we want
                            # classmethods to 'just work', so for this case, we pass in
                            # the wrapped's type
                            if isinstance(k, classmethod):
                                wrapped = get_wrapped(self) if wrapped is None else wrapped
                                return k.__get__(wrapped, type(wrapped))
                            else:
                                return k.__get__(self, type(self))
                    else:
                        # It's a data descriptor, so we invoke it unconditionally
                        if isinstance(k, classmethod):
                            wrapped = get_wrapped(self) if wrapped is None else wrapped
                            return k.__get__(wrapped, type(wrapped))
                        else:
                            return k.__get__(self, type(self))
                else:
                    try:
                        # if debug: print('getting csv_header')
                        wrapped = get_wrapped(self) if wrapped is None else wrapped
                        res = object.__getattribute__(wrapped, name)
                        # if debug: print('and we got it', res)
                        return res
                    except AttributeError:
                        return k

        return super(ContextualizingProxy, self).__getattribute__(name)

    def __setattr__(self, name, value):
        if name.startswith('_self_'):
            object.__setattr__(self, name, value)
        elif name == '__wrapped__':
            object.__setattr__(self, name, value)
            try:
                object.__delattr__(self, '__qualname__')
            except AttributeError:
                pass
            try:
                object.__setattr__(self, '__qualname__', value.__qualname__)
            except AttributeError:
                pass
        elif name == '__qualname__':
            setattr(get_wrapped(self), name, value)
            object.__setattr__(self, name, value)
        else:
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

        # print('WRAPPED CALL', self.__wrapped__.__call__.__func__)
        res = self.__wrapped__.__call__.__func__(self, *args, **kwargs)
        return res

    def __repr__(self):
        return 'ContextualizingProxy({}, {})'.format(repr(self._self_context),
                                                     repr(self.__wrapped__))


class ContextualizableClass(type):
    """ A super-type for contextualizable classes """

    def __getattribute__(self, name):
        return super(ContextualizableClass, self).__getattribute__('contextualize_class' if name == 'contextualize' else name)

    def contextualize_class(self, context):
        if context is None:
            return self
        _H = contextualize_metaclass(context, self)
        return _H('_H1', (self,), dict(class_context=context.identifier))


def is_data_descriptor(k):
    return hasattr(k, '__get__') and hasattr(k, '__set__')


def contextualized_new(ccls):
    def _helper(cls, *args, **kwargs):
        ores = super(ccls, cls).__new__(cls)
        if cls.context is not None:
            res = ores.contextualize(cls.context)
            # print('NEWING', cls, cls.context, id(ores), id(res))
            res.__init__ = type(ores).__init__.__get__(res, type(ores))
            type(ores).__init__(res, *args, **kwargs)
        else:
            res = ores
            # print('NEWING (None context)', cls, cls.context, id(ores), id(res))
        return res
    return _helper


def contextualize_helper(context, obj):
    """
    Does some extra stuff to make access to the type of a ContextualizingProxy
    work more-or-less like access to the the wrapped object
    """
    if context is None:
        return obj

    ctx = getattr(obj, 'context', None)
    if ctx is not None and ctx is context:
        # print('Already have this context', ctx)
        return obj

    ctx_proxy_typ = type(ContextualizingProxy)

    # Copy our special properties into the class so that they
    # always take precedence over attributes of the same name added
    # during construction of a derived class. This is to save
    # duplicating the implementation for them in all derived classes.

    pclass_dct = dict()
    # if hasattr(obj.__class__, 'rdf_type'):
        # print('occo', obj.__class__, obj.__class__.rdf_type)
    for k, v in vars(obj.__class__).items():
        if k not in ('__wrapped__', '__name__', '__doc__',
                     '__module__', '__weakref__', '__dict__',
                     '__init__'):
            # if is_mangled_name(k, obj.__class__):
                # demangle(k)
            if hasattr(v, '__get__'):
                pclass_dct[k] = v
            else:
                def myget(self, o, typ, k=k, oclass=obj.__class__):
                    # print('MYGET', self, type(o), typ)
                    if o is None:
                        res = getattr(oclass, k)
                        # print('MYGET', res)
                        return res
                    else:
                        # print('MYGET OOPS')
                        raise AttributeError()
                pclass_dct[k] = type('proxy_to_' + k, (object,), {'__get__': myget})()
    spclass_dct = dict()
    for k in dir(type(obj.__class__)):
        # XXX: Let's just be lazy here. We can refine the filtering later...
        if not (k.endswith('__') and k.startswith('__')):
            # These we assign directly.
            spclass_dct[k] = getattr(type(obj.__class__), k)
    new_ctx_proxy_typ = type('_I_' + ctx_proxy_typ.__name__, (ctx_proxy_typ,), spclass_dct)

    newtyp = new_ctx_proxy_typ('CtxProxyClass_' + obj.__class__.__name__,
                               (ContextualizingProxy,), pclass_dct)
    res = newtyp(context, obj)

    return res
