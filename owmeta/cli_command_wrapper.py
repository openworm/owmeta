from __future__ import print_function
import sys
import types
import argparse
import copy as _copy
from numpydoc.docscrape import FunctionDoc
from yarom.mapper import FCN
from .command_util import IVar, SubCommand


# TODO: Use `inspect` module for getting argument names so we aren't depending on docstrings
# TODO: Abstract numpydoc out into a hints provider (also implement a hints provider)
from .cli_common import (INSTANCE_ATTRIBUTE,
                         METHOD_NAMED_ARG,
                         METHOD_NARGS,
                         METHOD_KWARGS)

from .cli_hints import CLI_HINTS


class CLIUserError(Exception):
    pass


def _method_runner(runner, key):
    def _f(*args, **kwargs):
        return getattr(runner, key)(*args, **kwargs)
    return _f


def _sc_runner(sub_mapper, sub_runner):
    def _f():
        return sub_mapper.apply(sub_runner)
    return _f


class CLIArgMapper(object):
    '''
    Stores mappings for arguments and maps them back to the part of the object
    they come from
    '''
    def __init__(self):
        self.mappings = dict()
        self.methodname = None
        self.runners = dict()
        ''' Mapping from subcommand names to functions which run for them '''

        self.arg_count = dict()

        self.argparser = None

    def apply(self, runner):
        iattrs = self.get(INSTANCE_ATTRIBUTE)
        kvpairs = self.get(METHOD_KWARGS)
        kvs = list(kv.split('=') for kv in kvpairs.values())
        kvs += self.get(METHOD_NAMED_ARG).items()

        kwargs = {k: v for k, v in kvs}
        try:
            args = next(iter(self.get(METHOD_NARGS).values()))
        except StopIteration:
            args = ()

        runmethod = None

        if self.methodname:
            runmethod = self.runners.get(self.methodname, None)

        if runmethod is None:
            if callable(runner):
                runmethod = runner
            else:
                self.argparser.print_help(file=sys.stderr)
                print(file=sys.stderr)
                raise CLIUserError('Please specify a sub-command')

        for k, v in iattrs.items():
            setattr(runner, k, v)

        return runmethod(*args, **kwargs)

    def get(self, key):
        return {k[1]: self.mappings[k] for k in self.mappings if k[0] == key}

    def get0(self, key):
        return {k: self.mappings[k] for k in self.mappings if k[0] == key}

    def __str__(self):
        return type(self).__name__ + '(' + str(self.mappings) + ')'


class CLIStoreAction(argparse.Action):
    ''' Interacts with the CLIArgMapper '''

    def __init__(self, mapper, key, index=-1, *args, **kwargs):
        super(CLIStoreAction, self).__init__(*args, **kwargs)
        if self.nargs == 0:
            raise ValueError('nargs for store actions must be > 0; if you '
                             'have nothing to store, actions such as store '
                             'true or store const may be more appropriate')
        if self.const is not None and self.nargs != argparse.OPTIONAL:
            raise ValueError('nargs must be %r to supply const' % argparse.OPTIONAL)

        self.mapper = mapper
        self.key = key
        self.name = self.dest
        self.index = index

    def __call__(self, parser, namespace, values, option_string=None):
        self.mapper.mappings[(self.key, self.name, self.index)] = values
        setattr(namespace, self.dest, values)


class CLIStoreTrueAction(CLIStoreAction):
    def __init__(self, *args, **kwargs):
        super(CLIStoreTrueAction, self).__init__(*args, **kwargs)
        self.nargs = 0

    def __call__(self, parser, namespace, values, option_string=None):
        super(CLIStoreTrueAction, self).__call__(parser, namespace, True, option_string)


class CLIAppendAction(CLIStoreAction):
    def __call__(self, parser, namespace, values, option_string=None):
        items = _copy.copy(_ensure_value(namespace, self.dest, []))
        items.append(values)
        setattr(namespace, self.dest, items)


class CLISubCommandAction(argparse._SubParsersAction):
    def __init__(self, mapper, *args, **kwargs):
        super(CLISubCommandAction, self).__init__(*args, **kwargs)
        self.mapper = mapper

    def __call__(self, *args, **kwargs):
        if self.mapper.methodname is not None:
            raise ValueError('More than one sub command has been specified!'
                             'Attempted to set {} when {} had already been'
                             ' set.'.format(self.dest, self.mapper.methodname))

        self.mapper.methodname = args[2][0]
        super(CLISubCommandAction, self).__call__(*args, **kwargs)


NOT_SET = object()


def _ensure_value(namespace, name, value):
    if getattr(namespace, name, NOT_SET) is NOT_SET:
        setattr(namespace, name, value)
    return getattr(namespace, name)


class CLICommandWrapper(object):

    def __init__(self, runner, mapper=None):
        self.runner = runner
        self.mapper = CLIArgMapper() if mapper is None else mapper
        self.hints = CLI_HINTS.get(FCN(type(runner)), {})

    def extract_args(self, val):
        docstring = getattr(val, '__doc__', '')
        if not docstring:
            docstring = ''
        docstring = docstring.strip()
        npdoc = FunctionDoc(val)
        params = npdoc['Parameters']
        paragraphs = self._split_paras(docstring)
        if (len(paragraphs) == 1 and not params) or len(paragraphs) > 1:
            summary = paragraphs[0]
        else:
            summary = ''
        if params: # Assuming the Parameters section is the last 'paragraph'
            paragraphs = paragraphs[:-1]
        detail = '\n'.join(x for x in paragraphs if x)

        return summary, detail, params

    def _split_paras(self, docstring):
        paragraphs = []
        temp = ''
        for ln in docstring.split('\n'):
            ln = ln.strip()
            if ln:
                temp += '\n' + ln
            else:
                if temp:
                    paragraphs.append(temp.strip())
                temp = ''
        if temp:
            paragraphs.append(temp.strip())

        return paragraphs

    def parser(self, parser=None):
        if parser is None:
            doc = getattr(self.runner, '__doc__', None)
            if doc:
                cmd_summary, _, _ = self.extract_args(self.runner)
            else:
                cmd_summary = None
            parser = argparse.ArgumentParser(description=cmd_summary)
        self.mapper.argparser = parser
        for key, val in vars(self.runner).items():
            if not key.startswith('_') and key not in self.hints.get('IGNORE', ()):
                parser.add_argument('--' + key, help=key.__doc__)

        _sp = [None]

        def sp():
            if _sp[0] is None:
                _sp[0] = parser.add_subparsers(dest='subparser', mapper=self.mapper,
                                               action=CLISubCommandAction)
            return _sp[0]

        for key, val in sorted(vars(type(self.runner)).items()):
            if not key.startswith('_') and key not in self.hints.get('IGNORE', ()):
                if isinstance(val, (types.FunctionType, types.MethodType)):
                    sc_hints = self.hints.get(key) if self.hints else None
                    summary, detail, params = self.extract_args(val)

                    subparser = sp().add_parser(key, help=summary, description=detail)

                    self.mapper.runners[key] = _method_runner(self.runner, key)
                    argcount = 0
                    for pindex, param in enumerate(params):
                        action = CLIStoreAction
                        if param[1] == 'bool':
                            action = CLIStoreTrueAction

                        arg = param[0]
                        desc = ' '.join(param[2])
                        if arg.startswith('**'):
                            subparser.add_argument('--' + arg[2:],
                                                   action=CLIAppendAction,
                                                   mapper=self.mapper,
                                                   key=METHOD_KWARGS,
                                                   help=desc)
                        elif arg.startswith('*'):
                            subparser.add_argument(arg[1:],
                                                   action=action,
                                                   nargs='*',
                                                   key=METHOD_NARGS,
                                                   mapper=self.mapper,
                                                   help=desc)
                        else:
                            arg_hints = self._arg_hints(sc_hints, METHOD_NAMED_ARG, arg)
                            names = None if arg_hints is None else arg_hints.get('names')
                            if names is None:
                                names = ['--' + arg]
                            argument_args = dict(action=action,
                                                 key=METHOD_NAMED_ARG,
                                                 mapper=self.mapper,
                                                 index=pindex,
                                                 help=desc)
                            if arg_hints:
                                nargs = arg_hints.get('nargs')
                                if nargs is not None:
                                    argument_args['nargs'] = nargs

                            subparser.add_argument(*names,
                                                   **argument_args)
                        argcount += 1
                    self.mapper.arg_count[key] = argcount
                elif isinstance(val, property):
                    doc = getattr(val, '__doc__', None)
                    parser.add_argument('--' + key, help=doc,
                                        action=CLIStoreAction,
                                        key=INSTANCE_ATTRIBUTE,
                                        mapper=self.mapper)
                elif isinstance(val, SubCommand):
                    summary, detail, params = self.extract_args(val)
                    sub_runner = getattr(self.runner, key)
                    sub_mapper = CLIArgMapper()

                    self.mapper.runners[key] = _sc_runner(sub_mapper, sub_runner)

                    subparser = sp().add_parser(key, help=summary, description=detail)
                    type(self)(sub_runner, sub_mapper).parser(subparser)
                elif isinstance(val, IVar):
                    doc = getattr(val, '__doc__', None)
                    if val.default_value:
                        if doc:
                            doc += '. Default is ' + repr(val.default_value)
                        else:
                            doc = 'Default is ' + repr(val.default_value)
                    # NOTE: we have a default value from the val, but we don't
                    # set it here -- IVars return the defaults ... by default
                    arg_kwargs = dict(help=doc,
                                      action=CLIStoreAction,
                                      key=INSTANCE_ATTRIBUTE,
                                      mapper=self.mapper)
                    if val.value_type == bool:
                        arg_kwargs['action'] = CLIStoreTrueAction
                    parser.add_argument('--' + key, **arg_kwargs)

        return parser

    def _arg_hints(self, sc_hints, atype, key):
        return None if sc_hints is None else sc_hints.get((atype, key))

    def main(self, args=None, argument_callback=None, argument_namespace_callback=None):
        '''
        Runs in a manner suitable for being the 'main' method for a command
        line interface: parses arguments (as would be done with the result of
        `parser`) from sys.argv or the provided args list and executes the
        commands specified therein

        Parameters
        ----------
        args : list
            the argument list to parse. optional
        argument_callback : callable
            a callback to add additional arguments to the command line. optional
        '''

        parser = self.parser()
        if argument_callback:
            argument_callback(parser)
        ns = parser.parse_args(args=args)
        if argument_namespace_callback:
            argument_namespace_callback(ns)
        return self.mapper.apply(self.runner)
