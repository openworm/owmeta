import rdflib as R
from PyOpenWorm import DataUser, Configure

class DataObject(DataUser):
    def __init__(self,ident="",conf=False):
        DataUser.__init__(self,conf)
        self._id = ident
    def identifier(self):
        return R.URIRef(self._id)
