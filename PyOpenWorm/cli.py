from __future__ import print_function
import sys
import json
from tqdm import tqdm
import six
from .cli_command_wrapper import CLICommandWrapper, CLIUserError
from .command import POW, GenericUserError
from .git_repo import GitRepoProvider


def additional_args(parser):
    'Add some additional options specific to CLI'
    parser.add_argument('--output-mode', default='text',
            help='How to print the results of a command'
            ' (if any). Either "json" or "text" (the default)')
    parser.add_argument('--text-field-separator', default='\t',
            help='Separator to use between fields in text-mode output')
    parser.add_argument('--text-record-separator', default='\n',
            help='Separator to use between records in text-mode output')


class NSHandler(object):
    def __init__(self, **kwargs):
        self.opts = dict(kwargs)

    def __getitem__(self, k):
        return self.opts[k]

    def __getattr__(self, k):
        return self.opts[k]

    def __call__(self, ns):
        self.opts['output_mode'] = ns.output_mode
        self.opts['text_field_separator'] = ns.text_field_separator
        self.opts['text_record_separator'] = ns.text_record_separator


class JSONSerializer(object):
    def __call__(self, o):
        from rdflib.graph import Graph
        from PyOpenWorm.context import Context
        if isinstance(o, Graph):
            # eventually, we will use something like JSON-LD
            return []
        elif isinstance(o, Context):
            return {'identifier': o.identifier,
                    'base_namespace': o.base_namespace}
        else:
            return list(o)


def main():
    import logging
    logging.basicConfig()
    p = POW()
    p.log_level = 'WARN'
    p.message = print
    p.progress_reporter = tqdm
    p.repository_provider = GitRepoProvider()
    ns_handler = NSHandler()
    out = None
    try:
        out = CLICommandWrapper(p).main(argument_callback=additional_args,
                                        argument_namespace_callback=ns_handler)
    except (CLIUserError, GenericUserError) as e:
        s = str(e)
        if not s:
            from yarom.utils import FCN
            # In case someone forgets to add a helpful message for their user error
            s = 'Received error: ' + FCN(type(e))
        print(s, file=sys.stderr)
    output_mode = ns_handler.output_mode
    text_field_separator = ns_handler.text_field_separator
    text_record_separator = ns_handler.text_record_separator

    if out is not None:
        if output_mode == 'json':
            json.dump(out, sys.stdout, default=JSONSerializer(), indent=2)
        elif output_mode == 'text':
            if isinstance(out, dict):
                for k, v in out.items():
                    print('{}{}{}'.format(k, text_field_separator, v), end=text_record_separator)
            elif isinstance(out, six.string_types):
                print(out)
            else:
                try:
                    iterable = (x for x in out)
                except TypeError:
                    print(out)
                else:
                    for x in iterable:
                        print(x, end=text_record_separator)
