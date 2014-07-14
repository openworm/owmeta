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
    def __str__(self):
        return str(self.v)
    def __repr__(self):
        return str(self.v)


class BadConf(Exception):
    pass

class _link(ConfigValue):
    def __init__(self,members,c):
        self.members = members
        self.conf = c
    def get(self):
        return self.conf[self.members[0]]

class Configure(object):
    # conf: is a configure instance to base this one on
    # dependencies are required for this class to be initialized (TODO)

    def __init__(self, dependencies={}):
        self._properties = {}

    def __setitem__(self, pname, value):
        if not isinstance(value, ConfigValue):
            value = _C(value)
        if (pname in self._properties) and isinstance(self._properties[pname], _link):
            for x in self._properties[pname].members:
                self._properties[x] = value
        else:
            self._properties[pname] = value

    def __getitem__(self, pname):
        return self._properties[pname].get()

    def link(self,*names):
        """ Call link() with the names of configuration values that should
        always be the same to link them together
        """
        l = _link(names,self)
        for n in names:
            self._properties[n] = l

    def __contains__(self, thing):
        return (thing in self._properties)

    def __str__(self):
        return "\n".join("%s = %s" %(k,self._properties[k]) for k in self._properties)

    def __len__(self):
        return len(self._properties)

    @classmethod
    def open(cls,file_name):
        import json
        try:
            f = open(file_name)
            c = Configure()
            d = json.load(f)
            for k in d:
                c[k] = _C(d[k])
            f.close()
            return c
        except Exception, e:
            raise BadConf(e)

    def copy(self,other):
        if isinstance(other,Configure):
            self._properties = dict(other._properties)
        elif isinstance(other,dict):
            for x in other:
                self[x] = other[x]
        return self

    def get(self, pname, default=False):
        if pname in self._properties:
            return self._properties[pname].get()
        elif default:
            return default
        else:
            print self._properties
            raise KeyError(pname)

class Configureable(object):
    default = Configure()
    def __init__(self, conf=False):
        if not conf:
            self.conf = Configureable.default
        else:
            self.conf = conf

    def __getitem__(self,k):
        if not isinstance(self, Configure):
            return self.conf.get(k)
        else:
            return Configure.__getitem__(self,k)

    def __setitem__(self,k,v):
        if not isinstance(self, Configure):
            self.conf[k] = v
        else:
            return Configure.__setitem__(self,k,v)

    def get(self, pname, default=False):
        return self.conf.get(pname,default)
