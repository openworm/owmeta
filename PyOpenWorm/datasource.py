import six


class Informational(object):
    def __init__(self, name=None, display_name=None, value=None):
        self.name = name
        self.display_name = name if display_name is None else display_name
        self._value = value

    def __repr__(self):
        return 'Informational(name=\'' + self.name + \
                           '\', display_name=\'' + self.display_name + '\')'


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


class DataSource(six.with_metaclass(DataSourceType, object)):
    """ A source for data that can get translated into PyOpenWorm objects """
    def __init__(self, **kwargs):
        self.info_fields = list(self.__class__._info_fields)
        for k, v in kwargs.iteritems():
            if isinstance(v, Informational):
                info = v
                info.name = k
                v = info._value
                delattr(info, '_value')
                self.info_fields.append(info)
            else:
                self.info_fields.append(Informational(name=k))
            setattr(self, k, v)

    def __str__(self):
        return self.__class__.__name__ + '\n' + \
            '\n'.join('    ' + ': '.join((info.display_name,
                                         repr(getattr(self, info.name))))
                      for info in self.info_fields) + '\n'


class DataTranslator(object):
    """ Translates from a data source to PyOpenWorm objects """

    data_source_type = DataSource

    def get_data_objects(self, data_source):
        """ Override this to change how data objects are generated """
        if not isinstance(data_source, self.data_source_type):
            return set([])
        else:
            return self.translate(data_source)

    def translate(data_source):
        raise NotImplementedError()
