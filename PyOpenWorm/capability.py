'''
Defines 'capabilities', pieces of functionality that an object needs which must
be injected.

A given capability can be provided by more than one capability provider, but,
for a given set of providers, only one will be bound at a time. Logically, each
provider that provides the capability is asked, in a user-provided preference
order, whether it can provide the capability for the *specific* object and the
first one which can provide the capability is bound to the object.

The core idea is dependency injection: a capability does not modify the object:
the object receives the provider and an identifier for the capability provided,
but how the object uses the provider is up to the object. This is important
because the user of the object should not condition its behavior on the
particular capability provider used, although it may know about which
capabilities the object has.

Note, that there may be some providers that lose their ability to provide a
capability. This loss should be communicated with a 'CannotProvideCapability'
exception when the relevant methods are called on the provider. This *may* allow
certain operations to be retried with a provider lower on the capability order,
*but* a provider that throws CannotProvide may validly be asked if it can
provide the capability again -- if it *still* cannot provide the capability, it
should communicate that when asked.

Providers may keep state between calls to provide a capability, but their
correctness must not depend on any ordering of method calls except that, of
course, their ``__init__`` is called first.
'''
import six
from yarom.utils import FCN


class _Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            _Singleton._instances[cls] = super(_Singleton, cls).__call__(*args, **kwargs)
        return _Singleton._instances[cls]


class Capability(six.with_metaclass(_Singleton)):
    def __str__(self):
        return FCN(type(self))


class Provider(object):
    def provides(self, cap):
        '''
        Returns a SupportChecker if the provider provides for the given
        capability; otherwise, returns None
        '''
        if cap in getattr(self, 'provided_capabilities', ()):
            return self


class SupportChecker(object):

    def __call__(self, ob):
        ''' Returns an object that actually provides the capability '''
        return None

    def to(self, ob):
        ''' For use in a 'fluent' API.  Ex: a.provides(cap).to(obj) '''
        return self(ob)


class Capable(object):

    @property
    def needed_capabilities(self):
        return []

    def accept_capability_provider(self, cap, provider):
        '''
        The Capable should replace any previously accepted provider with the one
        given.
        '''
        raise NotImplementedError()


class CannotProvideCapability(Exception):
    '''
    Thrown by a *provider* when it cannot provide the capability during the
    object's execution
    '''
    def __init__(self, cap, provider):
        super(CannotProvideCapability, self).__init__('Provider, {}, cannot, now, provide the capability, {}'
                                                      .format(provider, cap))
        self._cap = cap
        self._provider = provider


class NoProviderAvailable(Exception):
    def __init__(self, cap, receiver=None):
        super(NoProviderAvailable, self).__init__('No providers currently provide {}{}'
                .format(cap, ' for ' + repr(receiver) if receiver else ''))
        self._cap = cap


class NoProviderGiven(Exception):
    def __init__(self, cap, receiver=None):
        super(NoProviderGiven, self).__init__('No {} providers were given{}'
                .format(cap, ' to ' + repr(receiver) if receiver else ''))
        self._cap = cap


def provide(ob, provs):
    if is_capable(ob):
        unsafe_provide(ob, provs)


def unsafe_provide(ob, provs):
    for cap in ob.needed_capabilities:
        provider = get_provider(ob, cap, provs)
        if not provider:
            raise NoProviderAvailable(cap, ob)
        ob.accept_capability_provider(cap, provider)


def get_providers(cap, provs):
    for p in provs:
        provfn = p.provides(cap)
        if provfn:
            yield p, provfn


def get_provider(ob, cap, provs):
    for p, provides_to in get_providers(cap, provs):
        provfn = provides_to(ob)
        if provfn:
            return provfn


def is_capable(ob):
    return isinstance(ob, Capable)
