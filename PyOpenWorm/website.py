from .document import BaseDocument


class Website(BaseDocument):

    """
    A representation of website

    Attributes
    ----------
    url : DatatypeProperty
        A URL for the website
    title : DatatypeProperty
        The official name for the website
    """
    def __init__(
            self,
            url=None,
            title=None,
            **kwargs):
        """
        Parameters
        ----------
        url : str
            A URL for the website
        title : str
            The official name for the website
        """
        super(Website, self).__init__(rdfs_comment=title, **kwargs)
        Website.DatatypeProperty('url', owner=self)
        Website.DatatypeProperty('title', owner=self)

        if url:
            self.url(url)

        if title:
            self.title(title)

    def defined_augment(self):
        return self.url.has_defined_value()

    def identifier_augment(self):
        return self.url.defined_values[0].identifier


__yarom_mapped_classes__ = (Website,)
