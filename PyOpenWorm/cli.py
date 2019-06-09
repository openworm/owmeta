from __future__ import print_function
import sys
import json
from tqdm import tqdm
import six
from .cli_command_wrapper import CLICommandWrapper, CLIUserError
from .command import POW, GenericUserError
from .git_repo import GitRepoProvider
from .text_util import format_table


def additional_args(parser):
    'Add some additional options specific to CLI'
    parser.add_argument('--output-mode', '-o', default='text',
            help='How to print the results of a command'
            ' (if any). Either "json" or "text" (the default)')
    parser.add_argument('--columns',
            help='Comma-separated list of columns to display in "table" output mode')
    parser.add_argument('--text-field-separator', default='\t',
            help='Separator to use between fields in "text" output mode')
    parser.add_argument('--text-record-separator', default='\n',
            help='Separator to use between records in "text" output mode')


NOT_SET = object()


class NSHandler(object):
    def __init__(self, **kwargs):
        self.opts = dict(kwargs)

    def __getitem__(self, k):
        return self.opts[k]

    def __getattr__(self, k, default=NOT_SET):
        if default is NOT_SET:
            try:
                return self.opts[k]
            except KeyError:
                raise AttributeError()
        else:
            return self.opts.get(k, default)

    def __call__(self, ns):
        self.opts['output_mode'] = ns.output_mode
        self.opts['text_field_separator'] = ns.text_field_separator
        self.opts['text_record_separator'] = ns.text_record_separator
        self.opts['columns'] = ns.columns

    def __str__(self):
        return 'NSHandler' + str(self.opts)


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


def _select(a, indexes):
    return [h for h, i in zip(a, range(len(a))) if i in indexes]


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
        return 1
    output_mode = ns_handler.output_mode
    text_field_separator = ns_handler.text_field_separator
    text_record_separator = ns_handler.text_record_separator

    if out is not None:
        if output_mode == 'json':
            json.dump(out, sys.stdout, default=JSONSerializer(), indent=2)
        elif output_mode == 'table':
            if getattr(out, 'columns', None):
                if ns_handler.columns:
                    selected_columns = [i for i, e in zip(range(len(out.header)), out.header)
                                        if e in ns_handler.columns.split(',')]
                elif out.default_columns:
                    selected_columns = [i for i, e in zip(range(len(out.header)), out.header)
                                        if e in out.default_columns]
                else:
                    selected_columns = list(range(len(out.header)))
            else:
                print('Tabular output is not supported for this command or there are no'
                      ' columns in the output')

                return 1
            header = _select(out.header, selected_columns)
            columns = _select(out.columns, selected_columns)

            def mygen():
                if columns:
                    for m in out:
                        yield tuple(c(m) for c in columns)
                else:
                    for m in out:
                        yield (m,)
            print(format_table(mygen(), header=header))
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
                        if hasattr(out, 'text_format'):
                            print(out.text_format(x), end=text_record_separator)
                        else:
                            print(x, end=text_record_separator)
