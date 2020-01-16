from rdflib.namespace import Namespace
from os.path import join as pth_join
from contextlib import contextmanager
from .common_data import DS_NS
from .local_file_ds import LocalFileDataSource
from .http_ds import HTTPFileDataSource
from ..mapper import mapped

from owmeta.datasource import Informational, DataTranslator
import csv


@mapped
class CSVDataSource(LocalFileDataSource):
    rdf_namespace = Namespace(DS_NS['CSVDataSource#'])

    csv_file_name = Informational(display_name='CSV file name',
                                  also=LocalFileDataSource.file_name)

    csv_header = Informational(display_name='Header column names', multiple=False)

    csv_field_delimiter = Informational(display_name='CSV field delimiter')


@mapped
class CSVHTTPFileDataSource(HTTPFileDataSource):
    rdf_namespace = Namespace(DS_NS['CSVHTTPFileDataSource#'])

    csv_header = Informational(display_name='Header column names', multiple=False)

    csv_field_delimiter = Informational(display_name='CSV field delimiter')


@mapped
class CSVDataTranslator(DataTranslator):

    def make_reader(self, source, skipheader=True, dict_reader=False, skiplines=0, **kwargs):
        params = dict()
        delim = source.csv_field_delimiter.one()

        if delim:
            params['delimiter'] = str(delim)

        params['skipinitialspace'] = True
        params.update(kwargs)

        @contextmanager
        def cm(skiplines, dict_reader):
            rel_fname = source.csv_file_name.one()
            fname = pth_join(source.basedir(), rel_fname)
            with open(fname) as f:
                while skiplines > 0:
                    next(f)
                    skiplines -= 1
                if dict_reader:
                    reader = csv.DictReader(f, **params)
                else:
                    reader = csv.reader(f, **params)
                if skipheader:
                    next(reader)
                yield reader
        return cm(skiplines, dict_reader)

    reader = make_reader
