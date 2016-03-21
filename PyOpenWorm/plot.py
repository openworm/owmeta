from PyOpenWorm import *


class Plot(DataObject):
    """
    Object for storing plot data in PyOpenWorm.

    Parameters
    ----------

    data : 2D list (list of lists)
        List of XY coordinates for this Plot.

    Example usage ::
        >>> pl = Plot([[1, 2], [3, 4]])
        >>> pl.get_data()
        # [[1, 2], [3, 4]]
    """

    def __init__(self, data=False, *args, **kwargs):
        DataObject.__init__(self, **kwargs)
        Plot.DatatypeProperty('_data_string', self, multiple=False)

        if data:
            self.set_data(data)

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

    def set_data(self, data):
        """
        Set the data attribute, which is user-facing,
        as well as the serialized _data_string
        attribute, which is used for db storage.
        """
        try:
            # make sure we're dealing with a 2D list
            assert isinstance(data, list)
            assert isinstance(data[0], list)
            self._data_string(self._to_string(data))
            self.data = data
        except (AssertionError, IndexError):
            raise ValueError('Attribute "data" must be a 2D list of numbers.')

    def get_data(self):
        """
        Get the data stored for this plot.
        """
        if self._data_string():
            return self._to_list(self._data_string())
        else:
            raise AttributeError('You must call "set_data" first.')
