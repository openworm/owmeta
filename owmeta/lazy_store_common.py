import re

STORE_PICKLE_FNAME_REGEX = re.compile(r'(?P<index>\d+)\.(?P<type>[ra])\.pickle')
''' Regex for the base name of a pickled store '''
