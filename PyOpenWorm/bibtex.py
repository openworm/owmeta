from .datasource import DataTranslator, DataSource
import bibtexparser
from bibtexparser.customization import author, link, doi


from PyOpenWorm.evidence import Evidence
from PyOpenWorm.document import Document


class BibTexDataSource(DataSource):

    def __init__(self, bibtex_file_name, **kwargs):
        super(BibTexDataSource, self).__init__(**kwargs)
        self.bibtex_file_name = bibtex_file_name


def tuplify(record):
    for val in record:
        if val not in ('ID',):
            if not isinstance(record[val], (list, tuple)):
                record[val] = (record[val],)
    return record


def customizations(record):
    """Use some functions delivered by the library

    :param record: a record
    :returns: -- customized record
    """
    return tuplify(doi(link(author(record))))


def parse_bibtex_into_evidence(file_name):
    res = dict()
    with open(file_name) as bibtex_file:
        parser = bibtexparser.bparser.BibTexParser()
        parser.customization = customizations
        bib_database = bibtexparser.load(bibtex_file, parser=parser)
        for entry in bib_database.entries:
            key = entry['ID']
            e = Document(key=key)

            for ath in entry.get('author', tuple()):
                e.author(ath)

            fields = ['title',
                      'year',
                      'author',
                      'doi',
                      ('link', 'uri')]
            for x in fields:
                if isinstance(x, tuple):
                    key, prop = x
                else:
                    prop = x
                    key = x
                for m in entry.get(key, tuple()):
                    getattr(e, prop)(m)

            res[key] = Evidence(reference=e)

    return res


class BibTexDataTranslator(DataTranslator):
    data_source_type = BibTexDataSource

    def translate(data_source):
        evidences = parse_bibtex_into_evidence(data_source.bibtex_file_name)
        return evidences.values()
