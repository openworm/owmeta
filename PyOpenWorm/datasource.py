import six
from collections import OrderedDict
from .identifier_mixin import IdMixin
from .context import Context


class Informational(object):
    def __init__(self, name=None, display_name=None, description=None, value=None, default_value=None):
        self.name = name
        self.display_name = name if display_name is None else display_name
        self.default_value = None
        self._value = value

    def __repr__(self):
        return ("Informational(name='{}',"
                " display_name='{}',"
                " default_value='{}')").format(self.name,
                                               self.display_name,
                                               self.default_value)


class DataSourceType(type):

    """A type for DataSources

    Sets up the graph with things needed for MappedClasses
    """
    def __init__(cls, name, bases, dct):
        super(DataSourceType, cls).__init__(name, bases, dct)
        cls._info_fields = []
        for z in dct:
            if z == 'metadata':
                for meta in dct[z]:
                    if isinstance(meta, Informational):
                        cls._info_fields.append(meta)

        for x in bases:
            if hasattr(x, '_info_fields'):
                cls._info_fields += x._info_fields


class DataSource(six.with_metaclass(DataSourceType, IdMixin())):
    """ A source for data that can get translated into PyOpenWorm objects """
    def __init__(self, **kwargs):
        self.info_fields = OrderedDict((i.name, i) for i in self.__class__._info_fields)
        for k, v in kwargs.items():
            if isinstance(v, Informational):
                # Any Informational we get must represent a *new* field, so we
                # raise a value error if one with the same name already exists
                if k in self.info_fields:
                    raise ValueError('The provided ad hoc field, "{}",'
                                     ' has already been declared by the class'.format(k))
                info = v
                info.name = k
                v = info._value
                delattr(info, '_value')
                self.info_fields[k] = info
            else:
                if k not in self.info_fields:
                    raise ValueError('Received a value for an undeclared field, "{}"'.format(k))
            setattr(self, k, v)
        for n, inf in self.info_fields.items():
            if not hasattr(self, n):
                setattr(self, n, inf.default_value)

    def __str__(self):
        return self.__class__.__name__ + '\n' + \
            '\n'.join('    ' + ': '.join((info.display_name,
                                         repr(getattr(self, info.name))))
                      for info in self.info_fields.values()) + '\n'


class DataObjectContextDataSource(DataSource):
    def __init__(self, context, **kwargs):
        super(DataObjectContextDataSource, self).__init__(**kwargs)
        if context is not None:
            self.context = context
        else:
            self.context = Context()


class DataTranslator(object):
    """ Translates from a data source to PyOpenWorm objects """

    input_type = DataSource
    output_type = DataSource

    def get_data_objects(self, data_source):
        """ Override this to change how data objects are generated """
        if not isinstance(data_source, self.input_type):
            return set([])
        else:
            return self.translate(data_source)

    def translate(data_source):
        raise NotImplementedError()
