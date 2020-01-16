from contextlib import contextmanager
from six.moves.urllib.request import urlopen
from ..datasource import Informational
from ..mapper import mapped
from .file_ds import FileDataSource


@mapped
class HTTPFileDataSource(FileDataSource):
    url = Informational(display_name='URL')

    @contextmanager
    def file_contents(self):
        return urlopen(self.url.one())
