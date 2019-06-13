from __future__ import print_function
import sys
import json
from tqdm import tqdm
import six
from .cli_command_wrapper import CLICommandWrapper, CLIUserError
from .command import POW, GenericUserError
from .git_repo import GitRepoProvider
from .text_util import format_table
from .command_util import GeneratorWithData


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


def die(message, status=1):
    print(message, file=sys.stderr)
    raise SystemExit(1)


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


def columns_arg_to_list(arg):
    return [s.strip() for s in arg.split(',')]


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
        die(s)
    output_mode = ns_handler.output_mode
    text_field_separator = ns_handler.text_field_separator
    text_record_separator = ns_handler.text_record_separator

    if out is not None:
        if output_mode == 'json':
            json.dump(out, sys.stdout, default=JSONSerializer(), indent=2)
        elif output_mode == 'table':
            # `out.header` holds the *names* for each column whereas `out.columns` holds
            # accessors for each column. `out` must have either:
            # 1) Just `header`
            # 2) `header` and `columns`
            # 3) neither `header` nor `columns`
            # at least one to be valid.
            #
            # If `out` has only `header`, then `header must have one element which is the
            # header for a single result from `out`.
            #
            # If it has `header` and `columns` then the two must be of equal length and
            # each element of `header` names the result of the corresponding entry in
            # `columns`.
            #
            # If neither `header` nor `columns` is given, then a default header of
            # `['Value']` is used and the column accessor is the identify function.
            #
            # `out.default_columns` determines which columns to show by default. If there
            # is no `default_columns`, then all defined columns are shown. The columns can
            # be overriden by the `--columns` command line argument. If there is no
            # `header`, but `--columns` is provided, the user will get an error.
            if getattr(out, 'columns', None) and getattr(out, 'header', None):
                if ns_handler.columns:
                    selected_columns = [i for i, e in zip(range(len(out.header)), out.header)
                                        if e in columns_arg_to_list(ns_handler.columns)]
                    if not selected_columns:
                        die('The given list of columns is not valid for this command')
                elif getattr(out, 'default_columns', None):
                    selected_columns = [i for i, e in zip(range(len(out.header)), out.header)
                                        if e in out.default_columns]
                else:
                    selected_columns = list(range(len(out.header)))
            elif getattr(out, 'columns', None):
                raise Exception('Programmer error: A header must be provided if an output'
                                ' has multiple columns')
            elif getattr(out, 'header', None):
                if len(out.header) != 1:
                    raise Exception('Programmer error: Only one column in the header can be defined if'
                                    ' no columns are defined')
                if ns_handler.columns \
                        and columns_arg_to_list(ns_handler.columns) != out.header:
                    die('The given list of columns is not valid for this command')
                out = GeneratorWithData(out,
                                        columns=[lambda x: x],
                                        header=out.header)
                selected_columns = [0]
            else:
                if ns_handler.columns:
                    die('The given list of columns is not valid for this command')
                out = GeneratorWithData(out,
                                        columns=[lambda x: x],
                                        header=['Value'])
                selected_columns = [0]

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
