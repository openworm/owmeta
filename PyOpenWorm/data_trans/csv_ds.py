from rdflib.namespace import Namespace
from os.path import join as pth_join
from contextlib import contextmanager
from .common_data import DS_NS
from .local_file_ds import LocalFileDataSource
from .http_ds import HTTPFileDataSource

from PyOpenWorm.datasource import Informational, DataTranslator
import csv


class CSVDataSource(LocalFileDataSource):
    rdf_namespace = Namespace(DS_NS['CSVDataSource#'])

    csv_file_name = Informational(display_name='CSV file name',
                                  also=LocalFileDataSource.file_name)

    csv_header = Informational(display_name='Header column names', multiple=False)

    csv_field_delimiter = Informational(display_name='CSV field delimiter')


class CSVHTTPFileDataSource(HTTPFileDataSource):
    rdf_namespace = Namespace(DS_NS['CSVHTTPFileDataSource#'])

    csv_header = Informational(display_name='Header column names', multiple=False)

    csv_field_delimiter = Informational(display_name='CSV field delimiter')


class CSVDataTranslator(DataTranslator):

    def make_reader(self, source, skipheader=True, **kwargs):
        params = dict()
        if source.csv_field_delimiter.has_defined_value():
            params['delimiter'] = str(source.csv_field_delimiter.onedef())

        params['skipinitialspace'] = True
        params.update(kwargs)

        @contextmanager
        def cm():
            rel_fname = source.csv_file_name.one()
            fname = pth_join(source.basedir(), rel_fname)
            with open(fname) as f:
                reader = csv.reader(f, **params)
                if skipheader:
                    next(reader)
                yield reader
        return cm()

    reader = make_reader


__yarom_mapped_classes__ = (CSVDataSource, CSVDataTranslator)
