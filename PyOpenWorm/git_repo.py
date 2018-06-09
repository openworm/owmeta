from git import Repo


class GitRepoProvider(object):

    def __init__(self):
        self._repo = None

    def init(self, base=None):
        self._repo = Repo.init(base)
