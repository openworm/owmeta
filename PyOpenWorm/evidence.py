"""
Created on Sun Feb 23 17:10:53 2014

@author: slarson
@author: mwatts15

An Evidence object represents a single document

"""
from PyOpenWorm import DataUser, Configure

class EvidenceError(BaseException):
    pass

class Evidence(DataUser):
    def __init__(self, **source):
        # Get the type of the evidence (a paper, a lab, a uri)
        # We keep track of a set of fields for the evidence.
        # Some of the fields are pulled from provided URIs and
        # some is provided by the user.
        #
        # Turns into a star graph
        #
        # Evidence field1 value1
        #        ; field2 value2
        #        ; field3 value3 .

        self._fields = dict()
        for k in source:
            if k in ('pubmed', 'pmid'):
                self._fields['pmid'] = source[k]
                break
            if k in ('wormbase', 'wbid'):
                self._fields['wormbase'] = source[k]
                break
            if k in ('bibtex'):
                self._fields['bibtex'] = source[k]
                break

    def add_data(self, k, v):
        """ Add a field

            :param k: Field name
            :param v: Field value
        """
        # Confirm that pmid contains a valid pubmed id
        self._fields[k] = v

    def asserts(self,stmt):
        stmt = tuple(x.identifier() for x in stmt[:3])
        update_stmt = "insert data { _:stmt ns1:subject <%s> ; ns1:predicate <%s> ; ns1:object <%s> ; ns1:asserts }"
    def author(self):
        return "Marcia"
