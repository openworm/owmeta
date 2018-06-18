import logging

from PyOpenWorm.dataObject import DataObject, ObjectProperty
from PyOpenWorm.contextDataObject import ContextDataObject

logger = logging.getLogger(__name__)


class EvidenceError(Exception):
    pass


class Evidence(DataObject):

    """
    A representation which provides evidence, for a group of statements.

    Attaching evidence to an set of statements is done like this::

       >>> from PyOpenWorm.connection import Connection
       >>> from PyOpenWorm.evidence import Evidence
       >>> from PyOpenWorm.context import Context

    Declare contexts::

       >>> ACTX = Context(ident="http://example.org/data/some_statements")
       >>> BCTX = Context(ident="http://example.org/data/some_other_statements")
       >>> EVCTX = Context(ident="http://example.org/data/some_statements#evidence")

    Make statements in `ACTX` and `BCTX` contexts::

       >>> ACTX(Connection)(pre_cell="VA11", post_cell="VD12", number=3)
       >>> BCTX(Connection)(pre_cell="VA11", post_cell="VD12", number=2)

    In `EVCTX`, state that a that a certain document supports the set of
    statements in `ACTX`, but refutes the set of statements in `BCTX`::

       >>> doc = EVCTX(Document)(author='White et al.', date='1986')
       >>> EVCTX(Evidence)(reference=doc, supports=ACTX.rdf_object)
       >>> EVCTX(Evidence)(reference=doc, refutes=BCTX.rdf_object)

    Finally, save the contexts::

       >>> ACTX.save_context()
       >>> BCTX.save_context()
       >>> EVCTX.save_context()

    One note about the `reference` predicate: the reference should, ideally, be
    an unambiguous link to a peer-reviewed piece of scientific literature
    detailing methods and data analysis that supports the set of statements.
    However, in gather data from pre-existing sources, going to that level of
    specificity may be difficult due to deficient query capability at the data
    source. In such cases, a broader reference, such as a `Website` with
    information which guides readers to a peer-reviewed article supporting the
    statement is sufficient.

    """

    class_context = 'http://openworm.org/schema/sci'

    supports = ObjectProperty(value_type=ContextDataObject)
    '''A context naming a set of statements which are supported by the attached
       reference'''

    refutes = ObjectProperty(value_type=ContextDataObject)
    '''A context naming a set of statements which are refuted by the attached
       reference'''

    reference = ObjectProperty()
    '''The resource providing evidence supporting/refuting the attached context'''

    def defined_augment(self):
        return ((self.supports.has_defined_value() or
                 self.refutes.has_defined_value()) and
                self.reference.has_defined_value())

    def identifier_augment(self):
        s = ""
        if self.supports.has_defined_value:
            s += self.supports.defined_values[0].identifier.n3()
        else:
            s += self.refutes.defined_values[0].identifier.n3()

        s += self.reference.defined_values[0].identifier.n3()
        return self.make_identifier(s)


__yarom_mapped_classes__ = (Evidence,)
