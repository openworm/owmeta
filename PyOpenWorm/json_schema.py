import copy
from pprint import pprint
import json
from PyOpenWorm.dataObject import DataObject, DatatypeProperty, ObjectProperty
from PyOpenWorm.datasource import DataSource, Informational
import PyOpenWorm.simpleProperty as SP
from jsonschema.validators import validator_for
from contextlib import contextmanager
from collections.abc import Sequence  # noqa
import re
from urllib.parse import unquote
from os.path import join as p
import logging


class AssignmentValidationException(Exception):
    pass


class Assigner(object):
    def __init__(self, schema):
        '''
        Takes a schema annotated with '_pow_type' entries indicating which types are
        expected at each position in the object and produces an instance of the root type
        described in the schema
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

    def create(self, instance, schema=None, ident=None):
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
            return self.create(instance, resolve_fragment(self.schema, sRef))

        sOneOf = schema.get('oneOf')
        if sOneOf:
            for opt in sOneOf:
                try:
                    return self.create(instance, opt)
                except AssignmentValidationException:
                    pass

        sType = schema.get('type')
        if isinstance(instance, str):
            if sType == 'string':
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
        elif isinstance(instance, bool):
            if sType == 'boolean':
                return instance
            raise AssignmentValidationException(sType, instance)
        elif isinstance(instance, list):
            if sType == 'array':
                item_schema = schema.get('items')
                if item_schema:
                    converted_list = list()
                    for idx, elt in enumerate(instance):
                        with self._pushing(idx):
                            converted_list.append(self.create(elt, item_schema))
                    return converted_list
                else:
                    # The default for items is to accept all, so we short-cut here...
                    # also means that there's POW type conversion
                    return instance
            raise AssignmentValidationException(sType, instance)
        elif isinstance(instance, dict):
            if sType == 'object':
                pow_type = schema.get('_pow_type')
                if pow_type:
                    pt_args = dict()
                    for k, v in instance.items():
                        props = schema.get('properties', {})
                        patprops = schema.get('patternProperties', {})
                        addprops = schema.get('additionalProperties', {})
                        default = schema.get('default', True)

                        if props:
                            sub_schema = props.get(k)
                            if sub_schema:
                                with self._pushing(k):
                                    pt_args[k] = self.create(v, sub_schema)
                                continue

                        if patprops:
                            found = False
                            for p in patprops:
                                if re.match(p, k):
                                    with self._pushing(k):
                                        pt_args[k] = self.create(v, patprops[p])
                                    found = True
                                    break
                            if found:
                                continue

                        if addprops:
                            with self._pushing(k):
                                pt_args[k] = self.create(v, addprops)
                            continue

                        if not default:
                            raise AssignmentValidationException(sType, instance, k, v)

                    res = pow_type(ident=self.gen_ident())
                    for k, v in pt_args.items():
                        if hasattr(res, k):
                            getattr(res, k)(v)
                        else:
                            # TODO: Do this properly...construct a property and set the
                            # value
                            pow_type.DatatypeProperty(k, owner=res)
                            getattr(res, k)(v)
                    return res
                else:
                    return None
        else:
            raise AssignmentValidationException(sType, instance)


class JSONSchemaTypeCreator(object):

    def __init__(self, name, schema, definition_base_name=''):
        '''
        Parameters
        ----------
        name : str
            The name of the root class and the base-name for all classes derived from a
            schema's properties
        schema : dict
            A JSON schema as would be translated by the :mod:`json` module
        definition_base_name : str
            The base-name for types defined in the schema's definitions. optional.
            By default, definitions just take the capitalized form of their key in the
            "definitions" block
        '''
        self.base_name = name
        self.definition_base_name = definition_base_name
        self.schema = schema

    def annotate(self):
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
            with self.processing_properties(path):
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

        typ = self.create_type(path)

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

    def _process_definitions(self, schema, path, references=None):
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


class DataSourceJSONSchemaTypeCreator(JSONSchemaTypeCreator):
    def __init__(self, *args, **kwargs):
        super(DataSourceJSONSchemaTypeCreator, self).__init__(*args, **kwargs)
        self.infos = dict()
        self.props = dict()

    @contextmanager
    def processing_properties(self, path):
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

    def create_type(self, path):
        doc = (schema.get('title', '') + '\n\n' +
               schema.get('description', '')).strip()
        if not path:
            infos = self.infos.get(path, dict())
            return type(DataSource)(self._extract_name(path),
                                    (DataSource,),
                                    dict(__doc__=doc,
                                         __module__=__name__,
                                         **infos))
        else:
            props = self.props.get(path, dict())
            return type(DataObject)(self._extract_name(path),
                                    (DataObject,),
                                    dict(__doc__=doc,
                                         __module__=__name__,
                                         **props))


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
