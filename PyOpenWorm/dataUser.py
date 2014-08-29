from rdflib import URIRef, Literal, Graph, Namespace, ConjunctiveGraph
from rdflib.namespace import RDFS, RDF, NamespaceManager
from .configure import Configureable,BadConf
import transaction
from .data import Data

__all__ = ["DataUser"]
class DataUser(Configureable):
    """ A convenience wrapper for users of the database

    Classes which use the database should inherit from DataUser.
    """
    def __init__(self, **kwargs):
        Configureable.__init__(self, **kwargs)
        if not isinstance(self.conf,Data):
            raise BadConf("Not a Data instance: "+ str(self.conf))
    @property
    def base_namespace(self):
        return self.conf['rdf.namespace']

    @base_namespace.setter
    def base_namespace_set(self, value):
        self.conf['rdf.namespace'] = value

    @property
    def rdf(self):
        return self.conf['rdf.graph']

    @rdf.setter
    def rdf(self, value):
        self.conf['rdf.graph'] = value

    def _remove_from_store(self, g):
        # Note the assymetry with _add_to_store. You must add actual elements, but deletes
        # can be performed as a query
        for group in grouper(g, 1000):
            temp_graph = Graph()
            for x in group:
                if x is not None:
                    temp_graph.add(x)
                else:
                    break
            s = " DELETE DATA {" + temp_graph.serialize(format="nt") + " } "
            L.debug("deleting. s = " + s)
            self.conf['rdf.graph'].update(s)

    def _add_to_store(self, g, graph_name=False):
        if self.conf['rdf.store'] == 'SPARQLUpdateStore':
            # XXX With Sesame, for instance, it is probably faster to do a PUT with over
            #     the endpoint's rest interface. Just need to do it for some common endpoints

            try:
                gs = g.serialize(format="nt")
            except:
                gs = _triples_to_bgp(g)

            if graph_name:
                s = " INSERT DATA { GRAPH "+graph_name.n3()+" {" + gs + " } } "
            else:
                s = " INSERT DATA { " + gs + " } "
                L.debug("update query = " + s)
                self.conf['rdf.graph'].update(s)
        else:
            gr = self.conf['rdf.graph']
            for x in g:
                gr.add(x)

        if self.conf['rdf.source'] == 'ZODB':
            # Commit the current commit
            transaction.commit()
            # Fire off a new one
            transaction.begin()

        #for group in grouper(g, int(self.conf.get('rdf.upload_block_statement_count',100))):
            #temp_graph = Graph()
            #for x in group:
                #if x is not None:
                    #temp_graph.add(x)
                #else:
                    #break
            #if graph_name:
                #s = " INSERT DATA { GRAPH "+graph_name.n3()+" {" + temp_graph.serialize(format="nt") + " } } "
            #else:
                #s = " INSERT DATA { " + temp_graph.serialize(format="nt") + " } "
            #L.debug("update query = " + s)
            #self.conf['rdf.graph'].update(s)

    def add_reference(self, g, reference_iri):
        """
        Add a citation to a set of statements in the database
        :param triples: A set of triples to annotate
        """
        new_statements = Graph()
        ns = self.conf['rdf.namespace']
        for statement in g:
            statement_node = self._reify(new_statements,statement)
            new_statements.add((URIRef(reference_iri), ns['asserts'], statement_node))

        self.add_statements(g + new_statements)

    #def _add_unannotated_statements(self, graph):
    # A UTC class.

    def retract_statements(self, graph):
        """
        Remove a set of statements from the database.
        :param graph: An iterable of triples
        """
        self._remove_from_store_by_query(graph)
    def _remove_from_store_by_query(self, q):
        import logging as L
        s = " DELETE WHERE {" + q + " } "
        L.debug("deleting. s = " + s)
        self.conf['rdf.graph'].update(s)

    def add_statements(self, graph):
        """
        Add a set of statements to the database.
        Annotates the addition with uploader name, etc
        :param graph: An iterable of triples
        """
        self._add_to_store(graph)

    def _reify(self,g,s):
        """
        Add a statement object to g that binds to s
        """
        n = self.conf['new_graph_uri'](s)
        g.add((n, RDF['type'], RDF['Statement']))
        g.add((n, RDF['subject'], s[0]))
        g.add((n, RDF['predicate'], s[1]))
        g.add((n, RDF['object'], s[2]))
        return n

def _triples_to_bgp(trips):
    # XXX: Collisions could result between the variable names of different objects
    g = " .\n".join(" ".join(_rdf_literal_to_gp(x) for x in y) for y in trips)
    return g

def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
    args = [iter(iterable)] * n
    while True:
        l = []
        try:
            for x in args:
                l.append(next(x))
        except:
            pass
        yield l
        if len(l) < n:
            break

def _rdf_literal_to_gp(x):
    return x.n3()

