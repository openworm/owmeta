"""
Common utilities for translation, massaging data, etc., that don't fit
elsewhere in owmeta
"""
import re

__all__ = ['normalize_cell_name']
# to normalize certain neuron and muscle names
SEARCH_STRING = re.compile(r'\w+0+[1-9]+')
REPLACE_STRING = re.compile(r'0+')
SEARCH_STRING_MUSCLE = re.compile(r'\w+BWM\w+')
REPLACE_STRING_MUSCLE = re.compile(r'BWM')


def normalize_cell_name(name):
    # normalize neuron and muscle names to match those used at other points
    # see #137 for elaboration
    # if there are zeroes in the middle of a name, remove them
    if re.match(SEARCH_STRING, name):
        name = REPLACE_STRING.sub('', name)
    name = normalize_muscle(name)
    name = name.upper()
    return name


def normalize_muscle(name):
    # normalize names of Body Wall Muscles
    # if there is 'BWM' in the name, remove it
    if re.match(SEARCH_STRING_MUSCLE, name):
        name = REPLACE_STRING_MUSCLE.sub('', name)
    return name
