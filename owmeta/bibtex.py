import bibtexparser

from .evidence import Evidence
from .bibtex_customizations import customizations


def bibtex_to_document(bibtex_entry, context=None):
    """ Takes a single BibTeX entry and translates it into a `.Document` object """
    from owmeta.document import Document

    res = Document.contextualize(context)()
    update_document_with_bibtex(res, bibtex_entry)
    return res


def update_document_with_bibtex(document, bibtex_entry):
    document.key = bibtex_entry['ID']
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
    '''
    Load BibTeX records from a string

    Parameters
    ----------
    bibtex_string : str
        Text of one or more BibTex records

    Returns
    -------
    bibtexparser.bibdatabase.BibDatabase
        Records represented in the string
    '''
    parser = make_default_bibtex_parser()
    return bibtexparser.loads(bibtex_string, parser=parser)


def load(bibtex_file):
    '''
    Load BibTeX records from a file

    Parameters
    ----------
    bibtex_file : :term:`file object`
        File containing one or more BibTex records

    Returns
    -------
    bibtexparser.bibdatabase.BibDatabase
        Records represented in the string
    '''
    parser = make_default_bibtex_parser()
    return bibtexparser.load(bibtex_file, parser=parser)


def load_from_file_named(file_name):
    '''
    Loads from a file with the given name

    Parameters
    ----------
    file_name : str
        Name of the bibtex file to open

    Returns
    -------
    bibtexparser.bibdatabase.BibDatabase
        Records from the named file
    '''
    with open(file_name) as bibtex_file:
        return load(bibtex_file)


def parse_bibtex_into_documents(file_name, context=None):
    '''
    Parses BibTeX records into a dictionary of `.Document` instances

    Parameters
    ----------
    bibtex_file : :term:`file object`
        File containing one or more BibTeX records

    Returns
    -------
    dict
        `.Document` instances from the records in the file
    '''
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
