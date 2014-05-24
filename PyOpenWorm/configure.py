# a class for modules that need outside objects to parameterize their behavior (because what are generics?)
# Modules inherit from this class and use their self['expected_configured_property']
class ConfigValue(object):
    def get(self):
        raise NotImplementedError

class _C(ConfigValue):
    def __init__(self, v):
        self.v = v
    def get(self):
        return self.v

class BadConf(BaseException):
    pass

class DoubleSet(BaseException):
    pass

class Configure:
    # conf: is a configure instance to base this one on
    # dependencies are required for this class to be initialized (TODO)
    def __init__(self, conf=False, dependencies={}):
        if not conf:
            self._properties = {}
        elif isinstance(conf, Configure):
            self._properties = dict(conf._properties)
        else:
            raise BadConf("Not a configuration object")

    def __setitem__(self, pname, value):
        if pname not in self._properties:
            if not isinstance(value, ConfigValue):
                value = _C(value)
            self._properties[pname] = value
        else:
            raise DoubleSet(pname)

    def __getitem__(self, pname):
        return self._properties[pname].get()

    def __contains__(self, thing):
        return (thing in self._properties)
    def pop(self, thing):
        return self._properties.pop(thing)
