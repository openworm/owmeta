# a class for modules that need outside objects to parameterize their behavior (because what are generics?)
# Modules inherit from this class and use their self['expected_configured_property']
import traceback
class ConfigValue(object):
    """ A value to be configured.  Base class intended to be subclassed, as its only method is not implemented
    """
    def get(self):
        raise NotImplementedError

class _C(ConfigValue):
    """ A helper class that simply stores a value and can report it back with the get method.
        Subclasses ConfigValue and implements the get method.
    """
    def __init__(self, v):
        self.v = v
    def get(self):
        return self.v
    def __str__(self):
        return str(self.v)
    def __repr__(self):
        return str(self.v)


class BadConf(Exception):
    """ Special exception subclass for alerting the user to a bad configuration
    """
    pass

class _link(ConfigValue):
    """ Helper class that groups values with configuration
    """
    def __init__(self,members,c):
        self.members = members
        self.conf = c
    def get(self):
        return self.conf[self.members[0]]

class Configure(object):
    """ A simple configuration object.  Enables setting and getting key-value pairs"""
    # conf: is a configure instance to base this one on
    # dependencies are required for this class to be initialized (TODO)

    def __init__(self, **initial_values):
        self._properties = dict()
        for x in initial_values:
            self._properties[x] = _C(initial_values[x])

    def __setitem__(self, pname, value):
        #if the value being put in is not an instance
        # of our ConfigValue, class, make it one.
        if not isinstance(value, ConfigValue):
            value = _C(value)
        if (pname in self._properties) and isinstance(self._properties[pname], _link):
            for x in self._properties[pname].members:
                self._properties[x] = value
        else:
            self._properties[pname] = value

    def __getitem__(self, pname):
        return self._properties[pname].get()

    def __iter__(self):
        return iter(self._properties)

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
        """
        Open a configuration file and read it to build the internal state.

        :param file_name: configuration file encoded as JSON
        :return: a Configure object with the configuration taken from the JSON file
        """
        import json

        f = open(file_name)
        c = Configure()
        d = json.load(f)
        for k in d:
            value = d[k]
            if isinstance(value,basestring):
                if value.startswith("BASE/"):
                    from pkg_resources import Requirement, resource_filename
                    value = value[4:]
                    value = resource_filename(Requirement.parse('PyOpenWorm'), value)
                    d[k] = value
            c[k] = _C(d[k])
        f.close()
        c['configure.file_location'] = file_name
        return c

    def copy(self,other):
        """
        Copy this configuration into a different object.

        :param other: A different configuration object to copy the configuration from this object into
        :return:
        """
        if isinstance(other,Configure):
            self._properties = dict(other._properties)
        elif isinstance(other,dict):
            for x in other:
                self[x] = other[x]
        return self

    def get(self, pname, default=False):
        """
        Get some parameter value out by asking for a key

        :param pname: they key of the value you want to return.
        :param default: True if you want the default value, False if you don't (default)
        :return: The value corresponding to the key in pname
        """
        if pname in self._properties:
            return self._properties[pname].get()
        elif default:
            return default
        else:
            raise KeyError(pname)

class Configureable(object):
    """ An object which can accept configuration.  A base class intended to be subclassed. """
    conf = Configure()
    default = conf
    def __init__(self, conf=False):
        pass

    def __getitem__(self,k):
        """
        Get a configuration value out by providing a key k

        :param k: the key for the value you wish to retrieve
        :return: the value you want to get back
        """
        return self.conf.get(k)

    def __setitem__(self,k,v):
        """
        Set a key - value pair on this object

        :param k: The key for the value to set
        :param v: The value to set
        :return: no return
        """
        self.conf[k] = v

    def get(self, pname, default=False):
        """
        The getter for the configuration

        :param pname: The key to retreive the value of interest
        :param default: True if you want the default value, False if you don't (default)
        :return: Returns the configuration value corresponding to the key pname.
        """
        return self.conf.get(pname,default)
