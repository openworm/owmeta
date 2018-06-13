import types
import argparse
from numpydoc.docscrape import FunctionDoc, ClassDoc
from .command_util import IVar


# TODO: Define a new namespace / actions such that we can store the origin of each argument
# TODO: Use the above namespace type / action processing to configure the `runner` to run


class CLICommandWrapper(object):

    def __init__(self, runner, mapper=None):
        self.runner = runner
        self.mapper = mapper

    def parser(self):
        parser = argparse.ArgumentParser()
        sp = parser.add_subparsers(dest='subparser')
        for key, val in vars(self.runner).items():
            if not key.startswith('_'):
                parser.add_argument('--' + key, help=key.__doc__)

        for key, val in sorted(vars(type(self.runner)).items()):
            if not key.startswith('_'):
                if isinstance(val, (types.FunctionType, types.MethodType)):
                    attr = getattr(val, '__doc__', None)
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

                    subparser = sp.add_parser(key, help=summary, description=detail)
                    for param in params:
                        action = None
                        if param[1] == 'bool':
                            action = 'store_true'
                        arg = param[0]
                        desc = ' '.join(param[2])
                        if arg.startswith('**'):
                            subparser.add_argument('--' + arg[2:],
                                                   action='append',
                                                   help=desc)
                        elif arg.startswith('*'):
                            subparser.add_argument(arg[1:],
                                                   action=action,
                                                   nargs='*',
                                                   help=desc)
                        else:
                            subparser.add_argument('--' + arg,
                                                   action=action,
                                                   help=desc)
                elif isinstance(val, property):
                    doc = getattr(val, '__doc__', None)
                    parser.add_argument('--' + key, help=doc)
                elif isinstance(val, IVar):
                    doc = getattr(val, '__doc__', None)
                    if val.default_value:
                        if doc:
                            doc += '. Default is ' + repr(val.default_value)
                        else:
                            doc = 'Default is ' + repr(val.default_value)
                    # NOTE: we have a default value from the val, but we don't
                    # set it here -- IVars return the defaults ... by default
                    parser.add_argument('--' + key, help=doc)

        return parser

    def main(self, args):
        '''
        Runs in a manner suitable for being the 'main' method for a command
        line interface: parses arguments (as would be done with the result of
        `parser`) from sys.argv or the provided args list and executes the
        commands specified therein
        '''
        ns = self.parser().parse_args()


