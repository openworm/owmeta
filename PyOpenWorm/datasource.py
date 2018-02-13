import six
from rdflib.term import URIRef
from rdflib.namespace import Namespace
from collections import OrderedDict, defaultdict
from .context import Context
from .dataObject import BaseDataObject


class Informational(object):
    def __init__(self, name=None, display_name=None, description=None,
                 value=None, default_value=None, identifier=None,
                 property_type='DatatypeProperty', multiple=True,
                 also=()):
        self.name = name
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
                if meta.identifier is None:
                    if self.rdf_namespace is not None:
                        meta.identifier = self.rdf_namespace[meta.name]
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

        super(DataSourceType, self).__init__(name, bases, newdct)

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

            # Make the property
            getattr(inf.cls, inf.property_type)(owner=self,
                                                linkName=inf.name,
                                                multiple=True,
                                                link=inf.identifier)
            ctxd_prop = self.context(getattr(self, inf.name))
            if v is not None:
                ctxd_prop(v)

    def defined_augment(self):
        return self.translation.has_defined_value()

    def identifier_augment(self):
        return self.make_identifier(self.translation.defined_values[0].identifier.n3())

    def __str__(self):
        try:
            return self.__class__.__name__ + '\n' + \
                '\n'.join('    ' + ': '.join((info.display_name,
                                             repr(list(getattr(self, info.name).defined_values))))
                          for info in self.info_fields.values()) + '\n'
        except AttributeError:
            return super(DataSource, self).__str__()


class Translation(BaseDataObject):
    """
    Representation of the method by which a DataSource was translated and
    the sources of that translation.  Unlike the 'source' field attached to
    DataSources, the Translation may distinguish different kinds of input
    source to a translation.
    """

    def __init__(self, translator, **kwargs):
        super(Translation, self).__init__(**kwargs)
        Translation.ObjectProperty('translator', owner=self)
        self.translator(translator)

    def defined_augment(self):
        return self.translator.has_defined_value() and self.translator.onedef().defined

    def identifier_augment(self):
        return self.make_identifier(self.translator.onedef().identifier.n3())


class DataObjectContextDataSource(DataSource):
    def __init__(self, context, **kwargs):
        super(DataObjectContextDataSource, self).__init__(**kwargs)
        if context is not None:
            self.context = context
        else:
            self.context = Context()


class DataTranslator(BaseDataObject):
    """ Translates from a data source to PyOpenWorm objects """

    input_type = DataSource
    output_type = DataSource
    translator_identifier = None

    def __init__(self):
        if self.translator_identifier is not None:
            super(DataTranslator, self).__init__(ident=self.translator_identifier)
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

    def make_translation(self):
        # print('MAKING TRANSLATION', id(self), self.context)
        return Translation.contextualize(self.context)(translator=self)

    def make_new_output(self, sources, *args, **kwargs):
        # print('making output_type', type(self), self.output_type)
        res = self.output_type(*args, translation=self.make_translation(), **kwargs)
        for s in sources:
            # print('setting source', s)
            res.contextualize(self.context).source(s)
        return res


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


__yarom_mapped_classes__ = (Translation, DataSource, DataTranslator)
