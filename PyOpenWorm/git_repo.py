from git import Repo


class GitRepoProvider(object):

    def __init__(self):
        self._repo = None
        self.base = None

    def init(self, base=None):
        base = self.base if not base else base
        self._repo = Repo.init(base)

    def add(self, files):
        self.repo().index.add(files)

    def remove(self, files, recursive=False):
        self.repo().index.remove(files, r=recursive)

    def reset(self):
        self.repo().index.reset()

    def commit(self, msg):
        self.repo().index.commit(msg)

    def repo(self):
        if self._repo is None:
            self._repo = Repo(self.base)
        return self._repo

    def clone(self, url, base):
        Repo.clone_from(url, base)

    @property
    def is_dirty(self):
        return self.repo().is_dirty()
