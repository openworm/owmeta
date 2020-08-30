from .. import BASE_SCHEMA_URL, BASE_DATA_URL
from rdflib.namespace import Namespace

TRANS_NS = Namespace(BASE_SCHEMA_URL + '/translators/')
TRANS_DATA_NS = Namespace(BASE_DATA_URL + '/translators/')
DS_NS = Namespace(BASE_SCHEMA_URL + '/data_sources/')
DS_DATA_NS = Namespace(BASE_DATA_URL + '/data_sources/')


class DSMixin(object):
    base_namespace = DS_NS
    base_data_namespace = DS_DATA_NS


class DTMixin(object):
    base_namespace = TRANS_NS
    base_data_namespace = TRANS_DATA_NS
