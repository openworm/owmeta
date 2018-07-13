from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals
import six
from pkg_resources import Requirement, resource_filename
import json
import re
from os import environ


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
        return repr(self.v)


class BadConf(Exception):

    """ Special exception subclass for alerting the user to a bad configuration
    """
    pass


class _link(ConfigValue):

    """ Helper class that groups values with configuration
    """

    def __init__(self, members, c):
        self.members = members
        self.conf = c

    def get(self):
        return self.conf[self.members[0]]


class NO_DEFAULT(object):
    def __repr__(self):
        return 'NO_DEFAULT'


NO_DEFAULT = NO_DEFAULT()


class Configure(object):

    """
    A simple configuration object.  Enables setting and getting key-value pairs

    Unlike a `dict`, Configure objects will execute a function when retrieving values to enable deferred computation of
    seldom-used configuration values. In addition, entries in a `Configure` can be aliased to one another.
    """
    # conf: is a configure instance to base this one on
    # dependencies are required for this class to be initialized (TODO)

    def __init__(self, **initial_values):
        self._properties = dict()
        for x in initial_values:
            self._properties[x] = _C(initial_values[x])

    def __setitem__(self, pname, value):
        # if the value being put in is not an instance
        # of our ConfigValue, class, make it one.
        if not isinstance(value, ConfigValue):
            value = _C(value)
        if (pname in self._properties) and isinstance(
                self._properties[pname], _link):
            for x in self._properties[pname].members:
                self._properties[x] = value
        else:
            self._properties[pname] = value

    def __getitem__(self, pname):
        return self._properties[pname].get()

    def __delitem__(self, pname):
        del self._properties[pname]

    def __iter__(self):
        return iter(self._properties)

    def link(self, *names):
        """ Call link() with the names of configuration values that should
        always be the same to link them together
        """
        link = _link(names, self)
        for n in names:
            self._properties[n] = link

    def __contains__(self, thing):
        return (thing in self._properties)

    def __str__(self):
        return "{\n"+(",\n".join(
            "\"%s\" : %s" %
            (k, repr(self._properties[k])) for k in self._properties)) + "\n}"

    def __len__(self):
        return len(self._properties)

    @classmethod
    def open(cls, file_name):
        """
        Open a configuration file and read it to build the internal state.

        :param file_name: configuration file encoded as JSON
        :return: a Configure object with the configuration taken from the JSON file
        """

        with open(file_name) as f:
            c = Configure()
            d = json.load(f)
            for k in d:
                value = d[k]
                if isinstance(value, six.string_types):
                    def matchf(md):
                        match = md.group(1)
                        # Note: We already matched the rest of the string, so
                        # we just need to check for the initial char here
                        valid_var_name = re.match(r'^[A-Za-z_]', match)
                        if valid_var_name:
                            res = environ.get(match, None)
                            res = None if res == '' else res
                        else:
                            raise ValueError("'%s' is an invalid env-var name\n"
                                             "Env-var names must be alphnumeric "
                                             "and start with either a letter or '_'" % match)
                        return res
                    res = re.sub(r'\$([A-Za-z0-9_]+)', matchf, value)
                    res = None if res == '' else res
                    d[k] = res
                    if value.startswith("BASE/"):
                        value = value[4:]
                        value = resource_filename(Requirement.parse('PyOpenWorm'), value)
                        d[k] = value
                c[k] = _C(d[k])
        c['configure.file_location'] = file_name
        return c

    def copy(self, other):
        """
        Copy this configuration into a different object.

        :param other: A different configuration object to copy the configuration from this object into
        :return:
        """
        if isinstance(other, Configure):
            self._properties = dict(other._properties)
        elif isinstance(other, dict):
            for x in other:
                self[x] = other[x]
        return self

    def get(self, pname, default=NO_DEFAULT):
        """
        Get some parameter value out by asking for a key.
        Note that unlike :py:class:`dict`, if you don't specify a default, then a :py:exc:`KeyError` is raised

        Parameters
        ----------
        pname : str
            they key of the value you want to return.
        default : object
            The default value to return if there's no entry for `pname`

        Returns
        -------
        The value corresponding to the key
        """
        val = self._properties.get(pname, None)
        if val is not None:
            return val.get()
        elif default is not NO_DEFAULT:
            return default
        else:
            raise KeyError(pname)


class ImmutableConfigure(Configure):
    def __setitem__(self, k, v):
        raise TypeError('\'{}\' object does not support item assignment'.format(repr(type(self))))


class Configureable(object):

    """ An object which can accept configuration. A base class intended to be subclassed. """
    default = ImmutableConfigure()

    def __init__(self, conf=None, **kwargs):
        super(Configureable, self).__init__(**kwargs)
        if conf is not None:
            if conf is self:
                raise ValueError('The \'conf\' of a Configureable cannot be itself')
            self.__conf = conf
        else:
            self.__conf = Configureable.default

    @property
    def conf(self):
        return self.__conf

    @conf.setter
    def conf(self, conf):
        self.__conf = conf

    def __getitem__(self, k):
        """
        Get a configuration value out by providing a key k

        :param k: the key for the value you wish to retrieve
        :return: the value you want to get back
        """
        return self.conf.get(k)

    def __setitem__(self, k, v):
        """
        Set a key - value pair on this object

        :param k: The key for the value to set
        :param v: The value to set
        :return: no return
        """
        self.conf[k] = v

    def get(self, pname, default=None):
        """
        Gets a config value from this :class:`Configureable`'s `conf`

        See Also
        --------
        Configure.get
        """
        if self.conf is self:
            raise ValueError('The \'conf\' of a Configureable cannot be itself')
        return self.conf.get(pname, default)
