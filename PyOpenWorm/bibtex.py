from .datasource import DataTranslator, DataSource
import bibtexparser
from bibtexparser.customization import link, doi


from PyOpenWorm.evidence import Evidence


def tuplify(record):
    for val in record:
        if val not in ('ID',):
            if not isinstance(record[val], (list, tuple)):
                record[val] = (record[val],)
    return record


def author(record):
    """
    Split author field by 'and' into a list of names.

    :param record: the record.
    :type record: dict
    :returns: dict -- the modified record.

    """
    if "author" in record:
        if record["author"]:
            record["author"] = [i.strip() for i in record["author"].replace('\n', ' ').split(" and ")]
        else:
            del record["author"]
    return record


def customizations(record):
    """Use some functions delivered by the library

    :param record: a record
    :returns: -- customized record
    """
    return tuplify(doi(link(author(record))))


def update_document_with_bibtex(document, bibtex_entry):
    document.set_key(bibtex_entry['ID'])
    for ath in bibtex_entry.get('author', tuple()):
        document.author(ath)

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
        for m in bibtex_entry.get(key, ()):
            getattr(document, prop)(m)


def bibtex_to_document(bibtex_entry):
    """ Takes a single BibTeX entry and translates it into a Document object """
    from PyOpenWorm.document import Document

    res = Document()
    update_document_with_bibtex(res, bibtex_entry)
    return res


def make_default_bibtex_parser():
    parser = bibtexparser.bparser.BibTexParser()
    parser.customization = customizations
    return parser


def loads(bibtex_string):
    parser = make_default_bibtex_parser()
    return bibtexparser.loads(bibtex_string, parser=parser)


def load(bibtex_file):
    parser = make_default_bibtex_parser()
    return bibtexparser.load(bibtex_file, parser=parser)


def load_from_file_named(file_name):
    with open(file_name) as bibtex_file:
        return load(bibtex_file)


def parse_bibtex_into_documents(file_name):
    res = dict()
    bib_database = load_from_file_named(file_name)
    for entry in bib_database.entries:
        entry_id = entry['ID']
        res[entry_id] = bibtex_to_document(entry)

    return res


def parse_bibtex_into_evidence(file_name):
    return {k: Evidence(reference=v)
            for k, v
            in parse_bibtex_into_documents(file_name).items()}


class BibTexDataSource(DataSource):

    def __init__(self, bibtex_file_name, **kwargs):
        super(BibTexDataSource, self).__init__(**kwargs)
        self.bibtex_file_name = bibtex_file_name


class BibTexDataTranslator(DataTranslator):
    data_source_type = BibTexDataSource

    def translate(data_source):
        evidences = parse_bibtex_into_evidence(data_source.bibtex_file_name)
        return evidences.values()
