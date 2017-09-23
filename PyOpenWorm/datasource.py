

class DataSource(object):
    """ A source for data that can get translated into PyOpenWorm objects """


class DataTranslator(object):
    """ Translates from a data source to PyOpenWorm objects """

    data_source_type = DataSource

    def get_data_objects(self, data_source):
        """ Override this to change how data objects are generated """
        if not isinstance(data_source, self.data_source_type):
            return set([])
        else:
            return self.translate(data_source)

    def translate(data_source):
        raise NotImplementedError()
