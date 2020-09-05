from owmeta_core.dataobject import DataObject
import rdflib as R

from . import BASE_BIO_DATA_URL, BASE_BIO_SCHEMA_URL


class BiologyType(DataObject):
    class_context = BASE_BIO_SCHEMA_URL

    base_namespace = R.Namespace(BASE_BIO_SCHEMA_URL + '/')
    base_data_namespace = R.Namespace(BASE_BIO_DATA_URL + '/')
