from __future__ import print_function
import sys
import types
import argparse
import copy as _copy
from numpydoc.docscrape import FunctionDoc
from .command_util import IVar, SubCommand


# TODO: Create a class that can provide hints for processing (e.g., treat
# positional arguments to this method as positional arguments on the command
# line)

INSTANCE_ATTRIBUTE = 'INSTANCE_ATTRIBUTE'
METHOD_NAMED_ARG = 'METHOD_NAMED_ARG'
METHOD_NARGS = 'METHOD_NARGS'
METHOD_KWARGS = 'METHOD_KWARGS'


class CLIUserError(Exception):
    pass


def _method_runner(runner, key):
    def _f(*args, **kwargs):
        getattr(runner, key)(*args, **kwargs)
    return _f


def _sc_runner(sub_mapper, sub_runner):
    def _f():
        sub_mapper.apply(sub_runner)
    return _f


class CLIArgMapper(object):
    '''
    Stores mappings for arguments and maps them back to the part of the object
    they come from
    '''
    def __init__(self):
        self.mappings = dict()
        self.methodname = None
        self.runfunc = None
        self.runners = dict()
        ''' Mapping from subcommand names to functions which run for them '''

        self.argparser = None

    def apply(self, runner):
        iattrs = self.get(INSTANCE_ATTRIBUTE)
        kvpairs = self.get(METHOD_KWARGS)
        kvs = list(kv.split('=') for kv in kvpairs.values())
        kvs += self.get(METHOD_NAMED_ARG).items()
        kwargs = {k: v for k, v in kvs}
        args = self.get(METHOD_NARGS).values()

        runmethod = None

        if self.methodname:
            runmethod = self.runners.get(self.methodname, None)
        elif self.runfunc:
            runmethod = self.runfunc

        if runmethod is None:
            if callable(runner):
                runmethod = runner
            else:
                self.argparser.print_help(file=sys.stderr)
                print(file=sys.stderr)
                raise CLIUserError("")

        for k, v in iattrs.items():
            setattr(runner, k, v)

        runmethod(*args, **kwargs)

    def get(self, key):
        return {k[1]: self.mappings[k] for k in self.mappings if k[0] == key}

    def __str__(self):
        return type(self).__name__ + '(' + str(self.mappings) + ')'


class CLIStoreAction(argparse.Action):
    ''' Interacts with the CLIArgMapper '''

    def __init__(self, mapper, key, *args, **kwargs):
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

    def __call__(self, parser, namespace, values, option_string=None):
        self.mapper.mappings[(self.key, self.name)] = values
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


class CLISubCommandMethodAction(argparse._SubParsersAction):
    def __init__(self, mapper, *args, **kwargs):
        super(CLISubCommandMethodAction, self).__init__(*args, **kwargs)
        self.mapper = mapper

    def __call__(self, *args, **kwargs):
        if self.mapper.methodname is not None:
            raise ValueError('More than one sub command has been specified!'
                             'Attempted to set {} when {} had already been'
                             ' set.'.format(self.dest, self.mapper.methodname))

        self.mapper.methodname = args[2][0]
        super(CLISubCommandMethodAction, self).__call__(*args, **kwargs)


def _ensure_value(namespace, name, value):
    if getattr(namespace, name, None) is None:
        setattr(namespace, name, value)
    return getattr(namespace, name)


class CLICommandWrapper(object):

    def __init__(self, runner, mapper=None):
        self.runner = runner
        self.mapper = CLIArgMapper() if mapper is None else mapper

    def extract_args(self, val):
        attr = getattr(val, '__doc__', '')
        if not attr:
            attr = ''
        attr = attr.strip()
        npdoc = FunctionDoc(val)
        params = npdoc['Parameters']
        lns = []
        temp = ''
        for ln in attr.split('\n'):
            ln = ln.strip()
            if ln:
                temp += '\n' + ln
            else:
                if temp:
                    lns.append(temp.strip())
                temp = ''
        if temp:
            lns.append(temp.strip())
        summary = lns[0] if len(lns) > 0 else ''
        if params:
            detail = '\n'.join(x for x in lns[:-1] if x)
        else:
            detail = '\n'.join(x for x in lns if x)

        return summary, detail, params

    def parser(self, parser=None):
        if parser is None:
            parser = argparse.ArgumentParser()
        self.mapper.argparser = parser
        sp = parser.add_subparsers(dest='subparser', mapper=self.mapper, action=CLISubCommandMethodAction)
        for key, val in vars(self.runner).items():
            if not key.startswith('_'):
                parser.add_argument('--' + key, help=key.__doc__)

        for key, val in sorted(vars(type(self.runner)).items()):
            if not key.startswith('_'):
                if isinstance(val, (types.FunctionType, types.MethodType)):
                    summary, detail, params = self.extract_args(val)

                    subparser = sp.add_parser(key, help=summary, description=detail)

                    self.mapper.runners[key] = _method_runner(self.runner, key)
                    for param in params:
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
                            subparser.add_argument('--' + arg,
                                                   action=action,
                                                   key=METHOD_NAMED_ARG,
                                                   mapper=self.mapper,
                                                   help=desc)
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

                    subparser = sp.add_parser(key, help=summary, description=detail)
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
                    parser.add_argument('--' + key, help=doc,
                                        action=CLIStoreAction,
                                        key=INSTANCE_ATTRIBUTE,
                                        mapper=self.mapper)

        return parser

    def main(self, args=None):
        '''
        Runs in a manner suitable for being the 'main' method for a command
        line interface: parses arguments (as would be done with the result of
        `parser`) from sys.argv or the provided args list and executes the
        commands specified therein
        '''
        self.parser().parse_args(args=args)
        try:
            self.mapper.apply(self.runner)
        except CLIUserError as e:
            print(e)
