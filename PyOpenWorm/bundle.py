
class BundleLoader(object):
    '''
    Loads a bundle.
    '''
    def __init__(self, base_directory=None):
        self.base_directory = base_directory

    def load(self, bundle_name):
        '''
        Loads a bundle into the given base directory
        '''
        raise NotImplementedError()
