from .dataObject import DataObject, DatatypeProperty


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

    _data_string = DatatypeProperty()

    def __init__(self, data=None, *args, **kwargs):
        super(Plot, self).__init__(*args, **kwargs)

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
        if input_string is None:
            return None

        out_list = []
        for pair_string in input_string.split('|'):
            pair_as_list = pair_string \
                .replace('[', '') \
                .replace(']', '') \
                .split(',')
            out_list.append([float(x) for x in pair_as_list])
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
        return self._to_list(self._data_string())


__yarom_mapped_classes__ = (Plot,)
