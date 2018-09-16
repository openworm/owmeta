from __future__ import print_function
import sys
import json
from tqdm import tqdm
from .cli_command_wrapper import CLICommandWrapper, CLIUserError
from .command import POW, GenericUserError
from .git_repo import GitRepoProvider


def main():
    p = POW()
    p.message = print
    p.progress_reporter = tqdm
    p.repository_provider = GitRepoProvider()
    try:
        out = CLICommandWrapper(p).main()
    except (CLIUserError, GenericUserError) as e:
        print(e, file=sys.stderr)
    import yarom
    def default(o):
        if isinstance(o, set):
            return list(o)
        else:
            try:
                return dict(o)
            except (ValueError, TypeError):
                try:
                    return list(o)
                except TypeError:
                    raise

            raise TypeError()

    if out is not None:
        json.dump(out, sys.stdout, default=default, indent=2)
