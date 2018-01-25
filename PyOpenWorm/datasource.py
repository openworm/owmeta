import six
from rdflib.term import URIRef
from rdflib.namespace import Namespace
from collections import OrderedDict
from .identifier_mixin import IdMixin
from .context import Context
from .dataObject import DataObject


class Informational(object):
    def __init__(self, name=None, display_name=None, description=None,
                 value=None, default_value=None, identifier=None):
        self.name = name
        self.display_name = name if display_name is None else display_name
        self.default_value = default_value
        self.description = description
        self._value = value
        self.identifier = identifier

    def __repr__(self):
        return ("Informational(name='{}',"
                " display_name={},"
                " default_value={},"
                " description={},"
                " identifier={})").format(self.name,
                                          repr(self.display_name),
                                          repr(self.default_value),
                                          repr(self.description),
                                          repr(self.identifier))


class DataSourceType(type):

    """A type for DataSources

    Sets up the graph with things needed for MappedClasses
    """
    def __init__(self, name, bases, dct):
        super(DataSourceType, self).__init__(name, bases, dct)
        self._info_fields = []
        for z in dct:
            if z == 'metadata':
                for meta in dct[z]:
                    if isinstance(meta, Informational):
                        if meta.identifier is None:
                            meta.identifier = self.rdf_namespace[meta.name]
                        self._info_fields.append(meta)

        for x in bases:
            if hasattr(x, '_info_fields'):
                self._info_fields += x._info_fields


class DataSource(six.with_metaclass(DataSourceType, IdMixin())):
    """
    A source for data that can get translated into PyOpenWorm objects.

    The value for any field can be passed to __init__ by name. Additionally, if
    the sub-class definition of a DataSource assigns a value for that field like::

        class A(DataSource):
            some_field = 3

    that value will be used over the default value for the field, but not over
    any value provided to __init__.
    """
    metadata = (Informational(name='translator', display_name='Translator',
                              description='The translator that constructed this data source'),
                Informational(name='source', display_name='Input source',
                              description='The data source that was translated into this one',
                              identifier=URIRef('http://openworm.org/schema/DataSource/source')))
    rdf_namespace = Namespace("http://openworm.org/entities/data_sources/DataSource#")

    def __init__(self, **kwargs):
        self.info_fields = OrderedDict((i.name, i) for i in self.__class__._info_fields)
        parent_kwargs = dict()
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
                    parent_kwargs[k] = v
                    continue
            setattr(self, k, v)
        super(DataSource, self).__init__(**parent_kwargs)
        for n, inf in self.info_fields.items():
            if not hasattr(self, n):
                setattr(self, n, inf.default_value)

    def defined_augment(self):
        return (self.source is not None and
                self.translator is not None and
                self.source.defined and
                self.translator.defined)

    def identifier_augment(self):
        return self.make_identifier(self.source.identifier.n3() + self.translator.identifier.n3())

    def __str__(self):
        return self.__class__.__name__ + '\n' + \
            '\n'.join('    ' + ': '.join((info.display_name,
                                         repr(getattr(self, info.name))))
                      for info in self.info_fields.values()) + '\n'


class Translation(DataObject):
    """
    Representation of the method by which a DataSource was translated and
    the sources of that translation.  Unlike the 'source' field attached to
    DataSources, the Translation may distinguish different kinds of input
    source to a translation.
    """

    def __init__(self, translator, **kwargs):
        super(Translation, self).__init__(**kwargs)
        self.translator = Translation.ObjectProperty()


class DataObjectContextDataSource(DataSource):
    def __init__(self, context, **kwargs):
        super(DataObjectContextDataSource, self).__init__(**kwargs)
        if context is not None:
            self.context = context
        else:
            self.context = Context()


class DataTranslator(IdMixin()):
    """ Translates from a data source to PyOpenWorm objects """

    input_type = DataSource
    output_type = DataSource
    translator_identifier = None

    def __init__(self):
        if type(self).translator_identifier is not None:
            super(DataTranslator, self).__init__(ident=type(self).translator_identifier)
        else:
            super(DataTranslator, self).__init__()

    def get_data_objects(self, data_source):
        """ Override this to change how data objects are generated """
        if not isinstance(data_source, self.input_type):
            return set([])
        else:
            return self.translate(data_source)

    def translate(self, data_source):
        raise NotImplementedError()

    def make_new_output(self, input_source, *args, **kwargs):
        return self.output_type(*args, source=input_source, translator=self, **kwargs)


class PersonDataTranslator(DataTranslator):
    """ A person who was responsible for carrying out the translation of a data source """

    def __init__(self, person):
        """
        Parameters
        ----------
        person : PyOpenWorm.dataObject.DataObject
            The person responsible for carrying out the translation.
        """
        self.person = person

    # No translate impl is provided here since this is intended purely as a descriptive object
