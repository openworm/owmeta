'''
`bibtexparser` customizations
'''
import re


HOWPUB_URL_RE = re.compile(r'\\url{([^}]+)}')


def customizations(record):
    """
    Standard owmeta `bibtexparser` customizations

    Includes: `url`, `note_url`, `doi`, `listify`, and `author`


    Parameters
    ----------
    record : dict
        the record

    Returns
    -------
    dict
        the given `record` with any updates applied
    """
    return url(note_url(doi(listify(author(record)))))


def listify_one(record, name):
    '''
    If the given field `name` does not have a `list` value, then updates the record by
    turning that value into a list.

    Parameters
    ----------
    record : dict
        The record to update
    name : str
        The name of the field to turn into a list

    Returns
    -------
    dict
        the given `record` with any updates applied
    '''
    if not isinstance(record[name], (list, tuple)):
        record[name] = [record[name]]
    elif isinstance(record[name], tuple):
        record[name] = list(record[name])
    return record


def listify(record):
    '''
    Turns every value in the record into a list except for ``ENTRYTYPE`` and ``ID``
    '''
    # Since some items can be multiples, it simplifies code in most places to
    # just make everything a list, even if it cannot appear more than once in
    # the properly formatted record.
    for val in record:
        if val not in ('ID', 'ENTRYTYPE'):
            listify_one(record, val)
    return record


def doi(record):
    """
    Adds a doi URI to the record if there's a ``doi`` entry in the record

    Parameters
    ----------
    record : dict
        the record to update

    Returns
    -------
    dict
        the given `record` with any updates applied
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
    Split author field by the string 'and' into a list of names.

    Parameters
    ----------
    record : dict
        the record

    Returns
    -------
    dict
        the given `record` with any updates applied
    """
    if "author" in record:
        if record["author"]:
            record["author"] = [i.strip() for i in record["author"].replace('\n', ' ').split(" and ")]
        else:
            del record["author"]
    return record


def note_url(record):
    '''
    Extracts URLs from ``note`` entries in the given record

    Parameters
    ----------
    record : dict
        the record

    Returns
    -------
    dict
        the given `record` with any updates applied
    '''
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
    r'''
    Merges any URL from ``\url{...}`` in ``howpublished``, and any existing ``link`` or
    ``url`` values in the record and normalizes them into a `list` in the ``url`` field of
    the record

    Parameters
    ----------
    record : dict
        the record

    Returns
    -------
    dict
        the given `record` with any updates applied
    '''

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
