from rdflib.namespace import Namespace
# from PyOpenWorm.datasource import Informational
from .common_data import DS_NS
from .http_ds import HTTPFileDataSource


class XLSXHTTPFileDataSource(HTTPFileDataSource):
    rdf_namespace = Namespace(DS_NS['XLSXHTTPFileDataSource#'])


__yarom_mapped_classes__ = (XLSXHTTPFileDataSource,)
