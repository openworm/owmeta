from PyOpenWorm import *


class Plot(DataObject):
    """
    Object for storing plot data in PyOpenWorm.

    Must be instantiated with a 2D list of coordinates.
    """

    def __init__(self, data=False, *args, **kwargs):
        DataObject.__init__(self, **kwargs)
        Plot.DatatypeProperty('_data_string', self, multiple=False)

        if (isinstance(data, list)) and (isinstance(data[0], list)):
            # data is user-facing, _data_string is for db
            self._data_string(self._to_string(data))
            self.data = data
        else:
            raise ValueError('Plot must be instantiated with 2D list.')

    def _to_string(self, input_list):
        """
        Converts input_list to a string
        for serialized storage in PyOpenWorm.
        """
        return '|'.join([str(item) for item in input_list])

    def _to_list(self, input_string):
        """
        Converts from internal serlialized string
        to a 2D list.
        """
        out_list = []
        for pair_string in input_string.split('|'):
            pair_as_list = pair_string \
                .replace('[', '') \
                .replace(']', '') \
                .split(',')
            out_list.append(
                map(float, pair_as_list)
            )
        return out_list

