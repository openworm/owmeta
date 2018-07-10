from __future__ import print_function
from .cli_command_wrapper import CLICommandWrapper
from .command import POW
from .git_repo import GitRepoProvider
from tqdm import tqdm


def main():
    p = POW()
    p.message = print
    p.progress_reporter = tqdm
    p.repository_provider = GitRepoProvider()
    CLICommandWrapper(p).main()
