from rdflib.namespace import Namespace
# from PyOpenWorm.datasource import Informational
from .common_data import DS_NS
from .http_ds import HTTPFileDataSource


class XLSXHTTPFileDataSource(HTTPFileDataSource):
    rdf_namespace = Namespace(DS_NS['XLSXHTTPFileDataSource#'])

    # column_headers = Informational(display_name='Header column names', multiple=False)

    # csv_field_delimiter = Informational(display_name='Field delimiter')
