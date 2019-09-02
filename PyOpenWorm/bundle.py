import re
from yarom.utils import FCN


class BundleLoader(object):
    '''
    Loads a bundle.
    '''
    def __init__(self, base_directory=None):
        self.base_directory = base_directory

    def load(self, bundle_name):
        '''
        Loads a bundle into the given base directory
        '''
        raise NotImplementedError()


class Descriptor(object):
    '''
    Descriptor for a bundle
    '''
    def __init__(self, name):
        self.name = name
        self.patterns = set([])
        self.includes = set([])

    @classmethod
    def make(cls, obj):
        '''
        Makes a descriptor from the given object.
        '''
        res = cls(name=obj['name'])
        res.patterns = set(make_pattern(x) for x in obj['patterns'])
        res.includes = set(make_include_func(x) for x in obj['includes'])
        return res


def make_pattern(s):
    if s.startswith('rgx:'):
        return RegexURIPattern(s[4:])
    else:
        return GlobURIPattern(s)


def make_include_func(s):
    s = s.strip()
    return lambda x: s == x


class URIPattern(object):
    def __init__(self, pattern):
        self._pattern = pattern

    def __call__(self, uri):
        return False

    def __str__(self):
        return '{}({})'.format(FCN(type(self)), self._pattern)


class RegexURIPattern(URIPattern):
    def __init__(self, pattern):
        super(RegexURIPattern, self).__init__(re.compile(pattern))

    def __call__(self, uri):
        # Cast the pattern match result to a boolean
        #print('comaparing uri', uri, 'to', self._pattern)
        return not not self._pattern.match(str(uri))


class GlobURIPattern(RegexURIPattern):
    def __init__(self, pattern):
        replacements = [
            ['*', '.*'],
            ['?', '.?'],
            ['[!', '[^']
        ]

        for a, b in replacements:
            pattern = pattern.replace(a, b)
        super(GlobURIPattern, self).__init__(re.compile(pattern))
