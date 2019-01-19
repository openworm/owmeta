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
    parser.add_argument('--output-mode', default='text')


class NSHandler(object):
    def __init__(self, **kwargs):
        self.opts = dict(kwargs)

    def __getitem__(self, k):
        return self.opts[k]

    def __getattr__(self, k):
        return self.opts[k]

    def __call__(self, ns):
        self.opts['output_mode'] = ns.output_mode


class JSONSerializer(object):
    def __call__(self, o):
        from rdflib.graph import Graph
        from PyOpenWorm.context import Context
        if isinstance(o, Graph):
            return 'eventually, we will use something like JSON-LD'
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

    if out is not None:
        if output_mode == 'json':
            json.dump(out, sys.stdout, default=JSONSerializer(), indent=2)
        elif output_mode == 'text':
            if isinstance(out, dict):
                for k, v in out.items():
                    print(k, v)
            elif isinstance(out, six.string_types):
                print(out)
            else:
                try:
                    for x in out:
                        print(x)
                except TypeError:
                    print(out)