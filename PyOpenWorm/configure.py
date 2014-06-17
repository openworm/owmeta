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


class BadConf(BaseException):
    pass

class Configureable:
    def __getitem__(self, k):
        return self.conf.get(k)

    def __setitem__(self, k, v):
        self.conf[k] = v

    def get(self, pname, default=False):
        return self.conf.get(pname,default)

    def __init__(self, conf=False):
        if not conf:
            self.conf = DefaultConfig
        elif isinstance(conf, Configure):
            self.conf = conf
        else:
            raise BadConf(self)

class Configure:
    # conf: is a configure instance to base this one on
    # dependencies are required for this class to be initialized (TODO)
    def __init__(self, dependencies={}):
        self._properties = {}

    def __setitem__(self, pname, value):
        if not isinstance(value, ConfigValue):
            value = _C(value)
        self._properties[pname] = value

    def __getitem__(self, pname):
        return self._properties[pname].get()

    def __contains__(self, thing):
        return (thing in self._properties)
    def __str__(self):
        return str(self._properties)

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
        else:
            raise BadConf()
        return self

    def get(self, pname, default=False):
        if pname in self._properties:
            return self._properties[pname].get()
        elif default:
            return default
        else:
            print _properties
            raise KeyError(pname)

DefaultConfig = Configure()
DefaultConfig['connectomecsv'] = 'https://raw.github.com/openworm/data-viz/master/HivePlots/connectome.csv'
DefaultConfig['neuronscsv'] = 'https://raw.github.com/openworm/data-viz/master/HivePlots/neurons.csv'
DefaultConfig['rdf.source'] = 'sparql_endpoint'
DefaultConfig['rdf.store_conf'] = ('http://107.170.133.175:8080/openrdf-sesame/repositories/OpenWorm','http://107.170.133.175:8080/openrdf-sesame/repositories/OpenWorm/statements')
def _k (a, x, y):
    raise NotImplementedError
DefaultConfig.__setiem__ = _k

