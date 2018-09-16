from contextlib import contextmanager
from rdflib.namespace import Namespace
from ..datasource import Informational
from .file_ds import FileDataSource
from .common_data import DS_NS


class LocalFileDataSource(FileDataSource):
    rdf_namespace = Namespace(DS_NS['LocalFileDataSource#'])
    file_name = Informational(display_name='File name')

    @contextmanager
    def file_contents(self):
        yield open(self.file_name.one(), 'b')


__yarom_mapped_classes__ = (LocalFileDataSource,)
