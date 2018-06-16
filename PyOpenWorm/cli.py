from .cli_command_wrapper import CLICommandWrapper
from .command import POW
from .git_repo import GitRepoProvider


def main():
    p = POW()
    p.repository_provider = GitRepoProvider()
    CLICommandWrapper(p).main()
