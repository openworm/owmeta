from __future__ import print_function
import six
from rdflib.term import URIRef
from rdflib.namespace import Namespace
from collections import OrderedDict, defaultdict
from yarom.mapper import FCN
from .context import Context
from .dataObject import BaseDataObject, ObjectProperty


class Informational(object):
    def __init__(self, name=None, display_name=None, description=None,
                 value=None, default_value=None, identifier=None,
                 property_type='DatatypeProperty', multiple=True,
                 property_name=None, also=()):
        self.name = name
        self._property_name = property_name
        self.display_name = name if display_name is None else display_name
        self.default_value = default_value
        self.description = description
        self._value = value
        self.identifier = identifier
        self.property_type = property_type
        self.multiple = multiple
        if also and not isinstance(also, (list, tuple)):
            also = (also,)
        self.also = also

        self.default_override = None
        """
        An override for the default value, typically set by setting the value
        in a DataSource class dictionary
        """

        self.cls = None

    @property
    def property_name(self):
        return self.name if self._property_name is None else self._property_name

    @property_name.setter
    def property_name(self, v):
        self._property_name = v

    def copy(self):
        res = type(self)()
        for x in vars(self):
            setattr(res, x, getattr(self, x))
        return res

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


class DuplicateAlsoException(Exception):
    pass


class DataSourceType(type(BaseDataObject)):

    """A type for DataSources

    Sets up the graph with things needed for MappedClasses
    """
    def __init__(self, name, bases, dct):
        self.__info_fields = []
        others = []
        newdct = dict()
        for z in dct:
            meta = dct[z]
            if isinstance(meta, Informational):
                meta.cls = self
                meta.name = z
                self.__info_fields.append(meta)
            else:
                others.append((z, dct[z]))

        for x in bases:
            if isinstance(x, DataSourceType):
                self.__info_fields += [inf.copy() for inf in x.__info_fields]

        for k, v in others:
            for i in range(len(self.__info_fields)):
                if self.__info_fields[i].name == k:
                    self.__info_fields[i] = self.__info_fields[i].copy()
                    self.__info_fields[i].default_override = v
                    break
            else: # no 'break'
                newdct[k] = v
        if not getattr(self, '__doc__', None):
            self.__doc__ = self._docstr()
        super(DataSourceType, self).__init__(name, bases, newdct)

    def _docstr(self):
        s = ''
        for inf in self.__info_fields:
            s += '{} : :class:`{}`'.format(inf.display_name, inf.property_type) + \
                    ('\n    Attribute: `{}`'.format(inf.name if inf.property_name is None else inf.property_name)) + \
                    (('\n\n    ' + inf.description) if inf.description else '') + \
                    ('\n\n    Default value: {}'.format(inf.default_value) if inf.default_value is not None else '') + \
                    '\n\n'
        return s

    @property
    def info_fields(self):
        return self.__info_fields


class DataSource(six.with_metaclass(DataSourceType, BaseDataObject)):
    '''
    A source for data that can get translated into PyOpenWorm objects.

    The value for any field can be passed to __init__ by name. Additionally, if
    the sub-class definition of a DataSource assigns a value for that field like::

        class A(DataSource):
            some_field = 3

    that value will be used over the default value for the field, but not over
    any value provided to __init__.
    '''

    source = Informational(display_name='Input source',
                           description='The data source that was translated into this one',
                           identifier=URIRef('http://openworm.org/schema/DataSource/source'),
                           property_type='ObjectProperty')

    translation = Informational(display_name='Translation',
                                description='Information about the translation process that created this object',
                                identifier=URIRef('http://openworm.org/schema/DataSource/translation'),
                                property_type='ObjectProperty')

    description = Informational(display_name='Description',
                                description='Free-text describing the data source')

    rdf_namespace = Namespace("http://openworm.org/entities/data_sources/DataSource#")

    def __init__(self, **kwargs):
        self.info_fields = OrderedDict((i.name, i) for i in self.__class__.info_fields)
        parent_kwargs = dict()
        new_kwargs = dict()
        for k, v in kwargs.items():
            if k not in self.info_fields:
                parent_kwargs[k] = v
            else:
                new_kwargs[k] = v
        super(DataSource, self).__init__(**parent_kwargs)
        vals = defaultdict(dict)
        for n, inf in self.info_fields.items():
            v = new_kwargs.get(n, None)
            if v is not None:
                vals[n]['i'] = v
            else:
                v = inf.default_value

            if inf.default_override is not None:
                vals[n]['e'] = inf.default_override

            vals[n]['d'] = inf.default_value

            for also in inf.also:
                if v is not None and vals[also.name].setdefault('a', v) != v:
                    raise DuplicateAlsoException('Only one also is allowed')

        for n, vl in vals.items():
            inf = self.info_fields[n]
            v = vl.get('i', vl.get('e', vl.get('a', vl['d'])))

            # Make the POW property
            #
            # We set the name for the property to the inf.name since that's how we access the info on this object, but
            # the inf.property_name is used for the linkName so that the property's URI is generated based on that name.
            # This allows to set an attribute named inf.property_name on self while still having access to the property
            # through inf.name.
            setattr(self,
                    inf.name,
                    getattr(inf.cls, inf.property_type)(owner=self,
                                                        linkName=inf.property_name,
                                                        multiple=True))
            ctxd_prop = getattr(self, inf.name).contextualize(self.context)
            if v is not None:
                ctxd_prop(v)

    def defined_augment(self):
        return self.translation.has_defined_value()

    def identifier_augment(self):
        return self.make_identifier(self.translation.defined_values[0].identifier.n3())

    def __str__(self):
        try:
            sio = six.StringIO()
            print(self.__class__.__name__, file=sio)
            for info in self.info_fields.values():
                print('    ' + info.display_name, end=': ', file=sio)
                for val in getattr(self, info.name).defined_values:
                    val_line_sep = '\n      ' + ' ' * len(info.display_name)
                    print(val_line_sep.join(str(val).split('\n')), end=' ', file=sio)
                print(file=sio)
            return sio.getvalue()
        except AttributeError:
            return super(DataSource, self).__str__()


class Translation(BaseDataObject):
    """
    Representation of the method by which a DataSource was translated and
    the sources of that translation.  Unlike the 'source' field attached to
    DataSources, the Translation may distinguish different kinds of input
    source to a translation.
    """

    translator = ObjectProperty()

    def defined_augment(self):
        return self.translator.has_defined_value() and self.translator.onedef().defined

    def identifier_augment(self):
        return self.make_identifier(self.translator.onedef().identifier.n3())


class GenericTranslation(Translation):
    """
    A generic translation that just has sources in order
    """

    source = ObjectProperty(multiple=True)

    def defined_augment(self):
        return super(GenericTranslation, self).defined_augment() and \
                self.source.has_defined_value()

    def identifier_augment(self):
        data = super(GenericTranslation, self).identifier_augment().n3() + \
                "".join(x.identifier.n3() for x in self.source.defined_values)
        return self.make_identifier(data)


class DataObjectContextDataSource(DataSource):
    def __init__(self, context, **kwargs):
        super(DataObjectContextDataSource, self).__init__(**kwargs)
        if context is not None:
            self.context = context
        else:
            self.context = Context()


def format_types(typ):
    if isinstance(typ, type):
        return ':class:`{}`'.format(FCN(typ))
    else:
        return ', '.join(':class:`{}`'.format(FCN(x)) for x in typ)


class DataTransatorType(type(BaseDataObject)):
    def __init__(self, name, bases, dct):
        super(DataTransatorType, self).__init__(name, bases, dct)

        if not getattr(self, '__doc__', None):
            self.__doc__ = '''Input type(s): {}\n
                              Output type(s): {}\n
                              URI: {}'''.format(format_types(self.input_type),
                                                format_types(self.output_type),
                                                self.translator_identifier)


class BaseDataTranslator(six.with_metaclass(DataTransatorType, BaseDataObject)):
    """ Translates from a data source to PyOpenWorm objects """

    input_type = DataSource
    output_type = DataSource
    translator_identifier = None
    translation_type = Translation

    def __init__(self):
        if self.translator_identifier is not None:
            super(BaseDataTranslator, self).__init__(ident=self.translator_identifier)
        else:
            super(BaseDataTranslator, self).__init__()

    def get_data_objects(self, data_source):
        """ Override this to change how data objects are generated """
        if not isinstance(data_source, self.input_type):
            return set([])
        else:
            return self.translate(data_source)

    def __call__(self, *args, **kwargs):
        self.output_key = kwargs.pop('output_key', None)
        try:
            return self.translate(*args, **kwargs)
        finally:
            self.output_key = None

    def translate(self, *args, **kwargs):
        '''
        Notionally, this method takes a data source, which is translated into
        some other data source. There doesn't necessarily need to be an input
        data source.
        '''
        raise NotImplementedError

    def make_translation(self, sources=()):
        '''
        It's intended that implementations of DataTranslator will override this
        method to make custom Translations according with how different
        arguments to Translate are (or are not) distinguished.

        The actual properties of a Translation subclass must be defined within
        the 'translate' method
        '''
        return self.translation_type.contextualize(self.context)(translator=self)

    def make_new_output(self, sources, *args, **kwargs):
        trans = self.make_translation(sources)
        res = self.output_type.contextualize(self.context)(*args, translation=trans,
                                                           key=self.output_key, **kwargs)
        for s in sources:
            res.contextualize(self.context).source(s)

        return res


class DataTranslator(BaseDataTranslator):
    """
    A specialization with the :class:`GenericTranslation` translation type that adds
    sources for the translation automatically when a new output is made
    """

    translation_type = GenericTranslation

    def make_translation(self, sources=()):
        res = super(DataTranslator, self).make_translation(sources)
        for s in sources:
            res.source(s)
        return res


class PersonDataTranslator(BaseDataTranslator):
    """ A person who was responsible for carrying out the translation of a data source """

    person = ObjectProperty(multiple=True)
    ''' A person responsible for carrying out the translation. '''

    # No translate impl is provided here since this is intended purely as a descriptive object


__yarom_mapped_classes__ = (Translation, DataSource, DataTranslator,
                            BaseDataTranslator, GenericTranslation, PersonDataTranslator)
