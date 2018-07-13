from rdflib.namespace import Namespace
from ..datasource import Informational, DataSource
from .common_data import DS_NS


class LocalFileDataSource(DataSource):
    rdf_namespace = Namespace(DS_NS['LocalFileDataSource#'])
    file_name = Informational(display_name='File name')


__yarom_mapped_classes__ = (LocalFileDataSource,)
