from .datasource import DataTranslator, DataSource
import re
import bibtexparser
from PyOpenWorm.evidence import Evidence


def listify_one(record, name):
    if not isinstance(record[name], (list, tuple)):
        record[name] = [record[name]]
    elif isinstance(record[name], tuple):
        record[name] = list(record[name])
    return record


def listify(record):
    # Since some items can be multiples, it simplifies code in most places to
    # just make everything a list, even if it cannot appear more than once in
    # the properly formatted record.
    for val in record:
        if val not in ('ID', 'ENTRYTYPE'):
            listify_one(record, val)
    return record


def doi(record):
    """

    :param record: the record.
    :type record: dict
    :returns: dict -- the modified record.

    """
    doi = record.get('doi')
    if doi is not None:
        if 'link' not in record:
            record['link'] = []
        for item in record['link']:
            if 'doi' in item:
                break
        else: # no break
            if not isinstance(doi, (list, tuple)):
                doi = [doi]

            for link in doi:
                if link.startswith('10'):
                    link = 'http://dx.doi.org/' + link
                record['link'].append(link)
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


HOWPUB_URL_RE = re.compile(r'\\url{([^}]+)}')


def note_url(record):
    note = record.get('note')
    if note is not None:
        for n in note:
            for u in HOWPUB_URL_RE.finditer(n):
                url = record.get('url')
                if url is None:
                    record['url'] = [u.group(1)]
                else:
                    listify_one(record, 'url')['url'].append(u.group(1))
    return record


def url(record):
    u = record.get('howpublished', '')
    md = HOWPUB_URL_RE.match(u)
    if md:
        v = record.get('url')
        if isinstance(v, tuple):
            record['url'] = list(v)

        if isinstance(v, list):
            v.append(md[1])

    url = record.get('url')
    link = record.get('link')

    if url is None:
        if isinstance(link, tuple):
            record['url'] = list(link)
        elif isinstance(link, list):
            record['url'] = link
        elif link is not None:
            record['url'] = [link]
        return record

    if isinstance(url, tuple):
        url = list(url)
        record['url'] = url

    if isinstance(url, list):
        if isinstance(link, (list, tuple)):
            url.extend(link)
        elif link is not None:
            url.append(link)

    return record


def customizations(record):
    """Use some functions delivered by the library

    :param record: a record
    :returns: -- customized record
    """
    return url(note_url(doi(listify(author(record)))))


def bibtex_to_document(bibtex_entry, context=None):
    """ Takes a single BibTeX entry and translates it into a Document object """
    from PyOpenWorm.document import Document

    res = Document.contextualize(context)()
    update_document_with_bibtex(res, bibtex_entry)
    return res


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


def make_default_bibtex_parser():
    parser = bibtexparser.bparser.BibTexParser(common_strings=True)
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


def parse_bibtex_into_documents(file_name, context=None):
    res = dict()
    bib_database = load_from_file_named(file_name)
    for entry in bib_database.entries:
        entry_id = entry['ID']
        res[entry_id] = bibtex_to_document(entry, context)

    return res


def parse_bibtex_into_evidence(file_name, context=None):
    return {k: Evidence.contextualize(context)(reference=v, supports=v.contextualize(context).as_context.rdf_object)
            for k, v
            in parse_bibtex_into_documents(file_name, context).items()}


class BibTexDataSource(DataSource):

    def __init__(self, bibtex_file_name, **kwargs):
        super(BibTexDataSource, self).__init__(**kwargs)
        self.bibtex_file_name = bibtex_file_name


class BibTexDataTranslator(DataTranslator):
    data_source_type = BibTexDataSource

    def translate(data_source):
        evidences = parse_bibtex_into_evidence(data_source.bibtex_file_name)
        return evidences.values()
