from __future__ import print_function
import rdflib
import logging
from itertools import groupby
from yarom.graphObject import (GraphObjectQuerier,
                               ZeroOrMoreTQLayer)
from .rdf_go_modifiers import SubClassModifier

L = logging.getLogger(__name__)


def goq_hop_scorer(hop):
    if hop[1] == rdflib.RDF.type:
        return 1
    return 0


def zomifier(target_type):
    def helper(rdf_type):
        if target_type == rdf_type:
            return SubClassModifier(rdf_type)
    return helper


def load(graph, start=None, target_type=None, context=None, idents=None):
    L.debug("load: graph %s start %s target_type %s context %s", graph, start, target_type, context)
    if idents is None:
        g = ZeroOrMoreTQLayer(zomifier(target_type), graph)
        idents = GraphObjectQuerier(start, g, parallel=False,
                                    hop_scorer=goq_hop_scorer)()

    if idents:
        choices = graph.triples_choices((list(idents),
                                         rdflib.RDF['type'],
                                         None))
        choices = list(choices)
        grouped_type_triples = groupby(choices, lambda x: x[0])
        hit = False
        for ident, type_triples in grouped_type_triples:
            hit = True
            types = set()
            for __, __, rdf_type in type_triples:
                types.add(rdf_type)
            tt = () if target_type is None else (target_type,)
            the_type = get_most_specific_rdf_type(types, context, bases=tt)
            yield oid(ident, the_type, context)
        if not hit:
            for ident in idents:
                tt = () if target_type is None else (target_type,)
                the_type = get_most_specific_rdf_type((), context, bases=tt)
                yield oid(ident, the_type, context)
    else:
        return


def get_most_specific_rdf_type(types, context=None, bases=()):
    """ Gets the most specific rdf_type.

    Returns the URI corresponding to the lowest in the DataObject class
    hierarchy from among the given URIs.
    """
    if context is None:
        if len(types) == 1 and (not bases or tuple(bases) == tuple(types)):
            return tuple(types)[0]
        if not types and len(bases) == 1:
            return tuple(bases)[0]
        msg = "Without a Context, `get_most_specific_rdf_type` cannot order RDF types {}{}".format(
                types,
                " constrained to be subclasses of {}".format(bases) if bases else '')
        L.warning(msg)
        return None

    mapper = context.mapper

    if bases:
        most_specific_types = tuple(y for y in (context.resolve_class(x) for x in bases) if y is not None)
        if not most_specific_types and mapper:
            most_specific_types = tuple(mapper.base_classes.values())
    elif mapper:
        most_specific_types = tuple(mapper.base_classes.values())
    else:
        most_specific_types = ()

    for x in types:
        try:
            class_object = context.resolve_class(x)
            if class_object is None:
                raise KeyError()
            if issubclass(class_object, most_specific_types):
                most_specific_types = (class_object,)
        except KeyError:
            L.warning(
                """A Python class corresponding to the type URI <{}> couldn't be found.
            You may want to import the module containing the class as well as
            add additional type annotations in order to resolve your objects to
            a more precise type.""".format(x))

    # XXX: Should we require that there's only one type at this point?
    if len(most_specific_types) == 1:
        return most_specific_types[0].rdf_type
    else:
        L.warning(('No most-specific type could be determined among {}'
                   ' constrained to subclasses of {}').format(types, bases))
        return None


def oid(identifier_or_rdf_type=None, rdf_type=None, context=None, base_type=None):
    """
    Create an object from its rdf type

    Parameters
    ----------
    identifier_or_rdf_type : :class:`str` or :class:`rdflib.term.URIRef`
        If `rdf_type` is provided, then this value is used as the identifier
        for the newly created object. Otherwise, this value will be the
        :attr:`rdf_type` of the object used to determine the Python type and
        the object's identifier will be randomly generated.
    rdf_type : :class:`str`, :class:`rdflib.term.URIRef`, :const:`False`
        If provided, this will be the :attr:`rdf_type` of the newly created
        object.

    Returns
    -------
       The newly created object

    """
    identifier = identifier_or_rdf_type
    if rdf_type is None:
        rdf_type = identifier_or_rdf_type
        identifier = None

    c = None
    if context is not None:
        c = context.resolve_class(rdf_type)

    if c is None:
        if base_type is None:
            from .dataObject import DataObject
            c = DataObject
        else:
            c = base_type
    L.debug("oid: making a {} with ident {}".format(c, identifier))

    # if its our class name, then make our own object
    # if there's a part after that, that's the property name
    o = None

    if context is not None:
        c = context(c)

    if identifier is not None:
        o = c(ident=identifier)
    else:
        o = c()
    return o
