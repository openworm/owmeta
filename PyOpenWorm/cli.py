from __future__ import print_function
import sys
import json
from tqdm import tqdm
from .cli_command_wrapper import CLICommandWrapper
from .command import POW
from .git_repo import GitRepoProvider


def main():
    p = POW()
    p.message = print
    p.progress_reporter = tqdm
    p.repository_provider = GitRepoProvider()
    out = CLICommandWrapper(p).main()
    if out is not None:
        json.dump(out, sys.stdout)
    import yarom
    def default(o):
        if isinstance(o, set):
            return list(o)
        else:
            raise TypeError()
    print(json.dumps(yarom.MAPPER.ModuleDependencies, default=default))
