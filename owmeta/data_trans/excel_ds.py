from rdflib.namespace import Namespace
from ..mapper import mapped
# from owmeta.datasource import Informational
from .common_data import DS_NS
from .http_ds import HTTPFileDataSource


@mapped
class XLSXHTTPFileDataSource(HTTPFileDataSource):
    rdf_namespace = Namespace(DS_NS['XLSXHTTPFileDataSource#'])
