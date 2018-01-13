from .dataObject import DataObject


class Website(DataObject):

    """
    A representation of website

    Attributes
    ----------
    url : DatatypeProperty
        A URL for the website
    """
    def __init__(
            self,
            url,
            **kwargs):
        """
        Parameters
        ----------
        url : string
            A URL for the website
        """
        super(Website, self).__init__(**kwargs)
        Website.DatatypeProperty('url', owner=self)

        if url is not None:
            self.url(url)

    def defined_augment(self):
        return self.url.has_defined_value()

    def identifier_augment(self):
        return self.url.defined_values[0].identifier
