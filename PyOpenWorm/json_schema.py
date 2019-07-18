import copy
from pprint import pprint
import json
from PyOpenWorm.dataObject import DataObject, DatatypeProperty, ObjectProperty
from PyOpenWorm.datasource import DataSource, Informational
from PyOpenWorm.utils import ellipsize
from PyOpenWorm.context import ClassContext
import PyOpenWorm.simpleProperty as SP
from contextlib import contextmanager
from collections.abc import Sequence  # noqa
import re
from urllib.parse import unquote
from os.path import join as p
import logging

L = logging.getLogger(__name__)


class ValidationException(Exception):
    pass


class AssignmentValidationException(ValidationException):
    pass


class Creator(object):
    '''
    Creates objects based on a JSON schema augmented with type annotations as would be
    produced by :py:class:`TypeCreator`

    Currently, only annotations for JSON objects are supported. In the future, conversions
    for all types (arrays, numbers, ints, strings) may be supported.
    '''

    def __init__(self, schema):
        '''
        Takes a schema annotated with '_pow_type' entries indicating which types are
        expected at each position in the object and produces an instance of the root type
        described in the schema

        Parameters
        ----------
        schema : dict
            The annotated schema
        '''
        self._path_stack = []
        self._root_identifier = None
        self.schema = schema

    @contextmanager
    def _pushing(self, path_component):
        self._path_stack.append(path_component)
        yield
        self._path_stack.pop()

    def gen_ident(self):
        if self._root_identifier:
            return self._root_identifier + '#' + '/'.join(self._path_stack)

    def assign(self, obj, key, val):
        '''
        Assigns values to properties on the created objects. If the `obj` does not already
        have a property for the given `key`, then it will be created. This is how
        ``additionalProperties`` and ``patternProperties`` are supported.
        '''
        if not hasattr(obj, key):
            typ = type(obj)
            if isinstance(val, (str, float, bool, int)) or \
                    isinstance(val, list) and val and \
                    isinstance(val[0], (str, float, bool, int)):
                typ.DatatypeProperty(key, owner=obj)
            elif isinstance(val, dict):
                L.warning("Received an object of unknown type: %s", ellipsize(str(val), 40))
                typ.DatatypeProperty(key, owner=obj)
            else:
                typ.ObjectProperty(key, value_type=type(val), owner=obj)
        getattr(obj, key)(val)

    def create(self, instance, context=None, ident=None):
        '''
        Creates an instance of the root POW type given a deserialized instance of the type
        described in our JSON schema.

        A context can be passed in and it will be used to contextualize the POW types


        Parameters
        ----------
        instance : dict
            The JSON object to create from
        context : PyOpenWorm.context.Context
            The context in which the object should be created
        '''
        self._context = context
        try:
            return self._create(instance, ident=ident)
        finally:
            del self._path_stack[:]
            self._root_identifier = None
            self._context = None

    def make_instance(self, pow_type):
        if self._context:
            pow_type = self._context(pow_type)
        return pow_type(ident=self.gen_ident())

    def _create(self, instance, schema=None, ident=None):
        if schema is None:
            schema = self.schema

        if ident is not None:
            self._root_identifier = ident

        if schema is False:
            raise AssignmentValidationException(schema, instance)

        if schema is True:
            return instance

        sRef = schema.get('$ref')

        if sRef:
            return self._create(instance, resolve_fragment(self.schema, sRef))

        sOneOf = schema.get('oneOf')
        if sOneOf:
            for opt in sOneOf:
                try:
                    return self._create(instance, opt)
                except AssignmentValidationException:
                    pass

        if instance is None:
            default = schema.get('default', None)
            # If the default is None, then it'll just fail below
            if default is not None:
                return self._create(default, schema)

        sType = schema.get('type')
        if isinstance(instance, str):
            if sType == 'string':
                return instance
            raise AssignmentValidationException(sType, instance)
        elif isinstance(instance, bool):
            # remember bool is a subtype of int, so boolean has to precede int
            if sType == 'boolean':
                return instance
            raise AssignmentValidationException(sType, instance)
        elif isinstance(instance, int):
            if sType in ('integer', 'number'):
                return instance
            raise AssignmentValidationException(sType, instance)
        elif isinstance(instance, float):
            if sType == 'number':
                return instance
            raise AssignmentValidationException(sType, instance)
        elif isinstance(instance, list):
            if sType == 'array':
                item_schema = schema.get('items')
                if item_schema:
                    converted_list = list()
                    for idx, elt in enumerate(instance):
                        with self._pushing(idx):
                            converted_list.append(self._create(elt, item_schema))
                    return converted_list
                else:
                    # The default for items is to accept all, so we short-cut here...
                    # also means that there's POW type conversion
                    return instance
            raise AssignmentValidationException(sType, instance)
        elif isinstance(instance, dict):
            if sType == 'object':
                pow_type = schema.get('_pow_type')
                if not pow_type:
                    # If an object isn't annotated, we treat as an error -- alternatives
                    # like returning None or just 'instance' could both be surprising and
                    # not annotating an object is most likely a mistake in a TypeCreator
                    # sub-class.
                    raise AssignmentValidationException(sType, instance)

                pt_args = dict()
                for k, v in instance.items():
                    props = schema.get('properties', {})

                    # If patprops doesn't have anything, then we pick it up with
                    # additionalProperties
                    patprops = schema.get('patternProperties', {})

                    # additionalProperties doesn't have any keys to check, so we
                    # can just pass true down to the next level
                    addprops = schema.get('additionalProperties', True)

                    if props:
                        sub_schema = props.get(k)
                        if sub_schema:
                            with self._pushing(k):
                                pt_args[k] = self._create(v, sub_schema)
                            continue

                    if patprops:
                        found = False
                        for p in patprops:
                            if re.match(p, k):
                                with self._pushing(k):
                                    pt_args[k] = self._create(v, patprops[p])
                                found = True
                                break
                        if found:
                            continue

                    if addprops:
                        with self._pushing(k):
                            pt_args[k] = self._create(v, addprops)
                        continue

                    raise AssignmentValidationException(sType, instance, k, v)

                # res must be treated as a black-box since sub-classes have total freedom
                # as far as what substitution they want to make
                res = self.make_instance(pow_type)
                for k, v in pt_args.items():
                    self.assign(res, k, v)
                return res
        else:
            raise AssignmentValidationException(sType, instance)

        def assign(self, obj, name, value):
            raise NotImplementedError()

        def make_instance(self, pow_type):
            raise NotImplementedError()


class TypeCreator(object):
    '''
    Creates POW types from a JSON schema and produces an copy of the schema annotated with
    the created types.

    The annontate method i
    '''

    def __init__(self, name, schema, definition_base_name=''):
        '''
        Parameters
        ----------
        name : str
            The name of the root class and the base-name for all classes derived from a
            schema's properties
        schema : dict
            A JSON schema as would be returned by :py:func:`json.load`
        definition_base_name : str
            The base-name for types defined in the schema's definitions. optional.
            By default, definitions just take the capitalized form of their key in the
            "definitions" block
        '''
        self.base_name = name
        self.definition_base_name = definition_base_name
        self.schema = schema

    def annotate(self):
        '''
        Returns the annotated JSON schema
        '''
        self._references = []
        return self._make_object(self.schema)

    def _handle_ref(self, path, v):
        if self._references is not None:
            self._references.append((path, v['$ref']))

    def _extract_name(self, path):
        s = self.base_name
        for idx, p in enumerate(path):
            if idx % 2 == 1:
                s += self._camelify(p.capitalize())
        return s

    def _camelify(self, s):
        # XXX: Should make more effort to ensure a valid identifier
        res = re.sub('_([a-zA-Z])', lambda mo: mo.group(1).upper(), s)
        res = re.sub('-([a-zA-Z])', lambda mo: mo.group(1).upper(), res)
        return res

    def _make_object(self, schema, path=()):
        annotated_definition_schemas = self._process_definitions(schema, path)

        annotated_property_schemas = None
        properties = schema.get('properties', None)
        if properties is not None:
            with self._processing_properties(path):
                annotated_property_schemas = {}
                for k, v in properties.items():
                    prop_type = None
                    if v.get('type') == 'object':
                        prop_annnotated_schema = self._make_object(v,
                                path=path + ('properties', k))
                    else:
                        prop_annnotated_schema = copy.deepcopy(v)

                    if '$ref' in v:
                        self._handle_ref(path, v)
                    annotated_property_schemas[k] = prop_annnotated_schema

                    self.proc_prop(path, k, v)

        typ = self.create_type(path, schema)

        annotated = copy.deepcopy(schema)

        if annotated_property_schemas is not None:
            annotated['properties'] = annotated_property_schemas

        if annotated_definition_schemas is not None:
            annotated['definitions'] = annotated_definition_schemas

        annotated['_pow_type'] = typ

        if path == ():
            for schema_path, reference in self._references:
                self._annotate_obj(annotated, schema_path,
                                   resolve_fragment(annotated, reference))

        return annotated

    def proc_prop(self, path, key, value):
        '''
        Process property named `key` with the given `value`.

        The `path` will not include the key but will be the path of the definition that
        contains the property. For example, in::

            {"$schema": "http://json-schema.org/schema",
             "title": "Example Schema",
             "type": "object",
             "properties": {"data": {"type": "object",
                                     "properties": {
                                        "data_data": {"type": "string"}
                                     }}}}

        `proc_prop` would be called as ``.proc_path((), 'data', {'type': 'object', ...})``
        for ``data``, but for ``data_data``, it would be called like
        ``.proc_path(('properties', 'data'), 'data_data', {'type': 'string'})``

        Parameters
        ----------
        path : tuple
            The path to the given property.
        key : str
            The name of the property
        value : dict
            the definition of the property
        '''
        raise NotImplementedError()

    def create_type(self, path, schema):
        '''
        Create the POW type.

        At this point, the properties for the schema will already be created.

        Parameters
        ----------
        path : tuple
            The path to the type
        schema : dict
            The JSON schema that applies to this type
        '''
        raise NotImplementedError()

    def _process_definitions(self, schema, path, references=None):
        # TODO: Actually use definition_base_name
        annotated_definition_schemas = None
        definitions = schema.get('definitions', None)
        if definitions:
            annotated_definition_schemas = {}
            for k, v in definitions.items():
                if v.get('type') == 'object':
                    defn_annnotated_schema = self._make_object(v,
                            path=path + ('definitions', k))
                elif '$ref' in v:
                    _handle_ref(path, v, references)
                else:
                    defn_annnotated_schema = copy.deepcopy(v)
                annotated_definition_schemas[k] = defn_annnotated_schema

        return annotated_definition_schemas

    @classmethod
    def _annotate_obj(self, obj, path, repl):
        if '_pow_type' not in repl:
            return

        if not path:
            obj['_pow_type'] = repl['_pow_type']

        subpart = obj.get(path[0])
        if subpart:
            self._annotate_obj(subpart, path[1:], repl)


class DataSourceTypeCreator(TypeCreator):
    def __init__(self, *args, context=None, **kwargs):
        super(DataSourceTypeCreator, self).__init__(*args, **kwargs)
        self.infos = dict()
        self.props = dict()
        if context and not isinstance(context, str):
            context = context.identifier

        if context is not None:
            self._context = ClassContext(ident=context)
        else:
            self._context = None

    @contextmanager
    def _processing_properties(self, path):
        if not path:
            self.infos[path] = {}
        else:
            self.props[path] = {}
        yield

    def proc_prop(self, path, k, v):
        if not path:
            info_type = 'DatatypeProperty'
            if v.get('type') == 'object':
                info_type = 'ObjectProperty'
            self.infos[path][k] = Informational(k, display_name=v.get('title'),
                                     description=v.get('description'),
                                     property_type=info_type)
        else:
            info_type = DatatypeProperty
            if v.get('type') == 'object':
                info_type = ObjectProperty
            self.props[path][k] = info_type()

    def create_type(self, path, schema):
        doc = (schema.get('title', '') + '\n\n' +
               schema.get('description', '')).strip()
        if not path:
            infos = self.infos.get(path, dict())
            dt = type(DataSource)(self._extract_name(path),
                                  (DataSource,),
                                  dict(__doc__=doc,
                                       __module__=__name__,
                                       class_context=self._context,
                                       **infos))
        else:
            props = self.props.get(path, dict())
            dt = type(DataObject)(self._extract_name(path),
                                  (DataObject,),
                                  dict(__doc__=doc,
                                       __module__=__name__,
                                       class_context=self._context,
                                       **props))
        if self._context is not None:
            self._context.mapper.process_class(dt)
        return dt


# Copied from jsonschema...don't want to handle all that shit yet.
def resolve_fragment(document, fragment):
    """
    Resolve a ``fragment`` within the referenced ``document``.

    Arguments:

        document:

            The referent document

        fragment (str):

            a URI fragment to resolve within it
    """
    _, fragment = fragment.split('#', 1)
    fragment = fragment.lstrip(u"/")
    parts = unquote(fragment).split(u"/") if fragment else []

    for part in parts:
        part = part.replace(u"~1", u"/").replace(u"~0", u"~")

        if isinstance(document, Sequence):
            # Array indexes should be turned into integers
            try:
                part = int(part)
            except ValueError:
                pass
        try:
            document = document[part]
        except (TypeError, LookupError) as e:
            raise Exception(
                "Unresolvable JSON pointer: %r" % fragment
            )

    return document
