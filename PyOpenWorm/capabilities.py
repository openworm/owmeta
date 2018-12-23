from .capability import Capability, Provider


class FilePathCapability(Capability):
    '''
    Provides a file path.
    '''


class FilePathProvider(Provider):
    provided_capabilities = [FilePathCapability()]

    def file_path(self):
        raise NotImplementedError()

# Possible other capabilities:
# - http/socks proxy
# - user name / password
