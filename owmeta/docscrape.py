'''
A replpacement for numpydoc's docscrape that doesn't require numpydoc's time-consuming
imports
'''
import re
from textwrap import dedent

parameter_regex = r'''
^(?P<param_name>[*]{0,2}\w+)(?:\s+:\s+(?P<param_type>.+))?\n
(?P<param_description>(^[ ]{4}(?:(\S.*|)\n))+)
'''

regex = r'''
(?P<desc>(?:(^\S.*)?\n)+(?:^\n+(?=Parameters)))?
(^Parameters\n
^-+\n
(?P<parameters>(?:{parameter_regex})+))?
'''.format(parameter_regex=parameter_regex)

first_line_unindented_regex = r'^\S.*\n+(?P<initial_white_space>\s+)'

RE = re.compile(regex, flags=re.VERBOSE | re.MULTILINE)
ParamRE = re.compile(parameter_regex, flags=re.VERBOSE | re.MULTILINE)
FLURE = re.compile(first_line_unindented_regex, flags=re.VERBOSE | re.MULTILINE)


def parse(text):
    resp = {}
    iws_match = FLURE.match(text)
    if iws_match:
        text = iws_match.group('initial_white_space') + text
    if text.startswith('\n'):
        text = text[1:]
    text = dedent(text)
    md = RE.match(text)
    if md:
        desc = md.group('desc')
        resp['desc'] = desc and desc.strip()
        resp['parameters'] = []
        params = md.group('parameters')
        if params:
            for pmd in ParamRE.finditer(params):
                param_type = pmd.group('param_type')
                tp = (pmd.group('param_name').strip(),
                      param_type and param_type.strip(),
                      pmd.group('param_description').strip())
                resp['parameters'].append(tp)
    if not resp.get('desc') and not resp.get('parameters'):
        resp['desc'] = text.strip()
    return resp
