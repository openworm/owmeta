import rdflib as R
from yarom.mapper import FCN
from yarom.go_modifiers import ZeroOrMore
from yarom.rdfUtils import UP


class SubClassModifier(ZeroOrMore):

    def __init__(self, rdf_type):
        super(SubClassModifier, self).__init__(rdf_type, R.RDFS.subClassOf, UP)

    def __repr__(self):
        return FCN(type(self)) + '(' + repr(self.identifier) + ')'
