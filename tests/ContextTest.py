import rdflib
from rdflib.term import URIRef, Variable
from PyOpenWorm.dataObject import DataObject, InverseProperty
from PyOpenWorm.context import Context
from PyOpenWorm.context_store import ContextStore
from .DataTestTemplate import _DataTest
try:
    from unittest.mock import MagicMock, Mock
except ImportError:
    from mock import MagicMock, Mock


class ContextTest(_DataTest):
    def test_inverse_property_context(self):
        class A(DataObject):
            def __init__(self, **kwargs):
                super(A, self).__init__(**kwargs)
                self.a = A.ObjectProperty(value_type=B)

        class B(DataObject):
            def __init__(self, **kwargs):
                super(B, self).__init__(**kwargs)
                self.b = B.ObjectProperty(value_type=A)
        InverseProperty(B, 'b', A, 'a')
        ctx1 = Context(ident='http://example.org/context_1')
        ctx2 = Context(ident='http://example.org/context_2')
        a = ctx1(A)(ident='a')
        b = ctx2(B)(ident='b')
        a.a(b)
        expected = (URIRef('b'), URIRef('http://openworm.org/entities/B/b'), URIRef('a'))
        self.assertIn(expected, list(ctx1.contents_triples()))

    def test_defined(self):
        class A(DataObject):
            def __init__(self, **kwargs):
                super(A, self).__init__(**kwargs)
                self.a = A.ObjectProperty(value_type=B)

            def defined_augment(self):
                return self.a.has_defined_value()

            def identifier_augment(self):
                return self.make_identifier(self.a.onedef().identifier.n3())

        class B(DataObject):
            def __init__(self, **kwargs):
                super(B, self).__init__(**kwargs)
                self.b = B.ObjectProperty(value_type=A)
        InverseProperty(B, 'b', A, 'a')
        ctx1 = Context(ident='http://example.org/context_1')
        ctx2 = Context(ident='http://example.org/context_2')
        a = ctx1(A)()
        b = ctx2(B)(ident='b')
        a.a(b)
        self.assertTrue(a.defined)

    def test_save_context_no_graph(self):
        ctx = Context()
        del ctx.conf['rdf.graph']
        with self.assertRaisesRegexp(Exception, r'graph'):
            ctx.save_context()

    def test_context_store(self):
        class A(DataObject):
            pass

        ctx = Context(ident='http://example.com/context_1')
        ctx(A)(ident='anA')
        self.assertIn(URIRef('anA'),
                      tuple(x.identifier for x in ctx.query(A)().load()))

    def test_decontextualize(self):
        class A(DataObject):
            pass
        ctx = Context(ident='http://example.com/context_1')
        ctxda = ctx(A)(ident='anA')
        self.assertIsNone(ctxda.decontextualize().context)

    def test_init_imports(self):
        ctx = Context(ident='http://example.com/context_1')
        self.assertEqual(len(list(ctx.imports)), 0)

    def test_zero_imports(self):
        ctx0 = Context(ident='http://example.com/context_0')
        ctx = Context(ident='http://example.com/context_1')
        ctx.save_imports(ctx0)
        self.assertEqual(len(ctx0), 0)

    def test_save_import(self):
        ctx0 = Context(ident='http://example.com/context_0')
        ctx = Context(ident='http://example.com/context_1')
        new_ctx = Context(ident='http://example.com/context_1')
        ctx.add_import(new_ctx)
        ctx.save_imports(ctx0)
        self.assertEqual(len(ctx0), 1)

    def test_add_import(self):
        ctx0 = Context(ident='http://example.com/context_0')
        ctx = Context(ident='http://example.com/context_1')
        ctx2 = Context(ident='http://example.com/context_2')
        ctx2_1 = Context(ident='http://example.com/context_2_1')
        ctx.add_import(ctx2)
        ctx.add_import(ctx2_1)
        ctx3 = Context(ident='http://example.com/context_3')
        ctx3.add_import(ctx)
        final_ctx = Context(ident='http://example.com/context_1', imported=(ctx3,))
        final_ctx.save_imports(ctx0)
        self.assertEqual(len(ctx0), 4)

    def test_init_len(self):
        ctx = Context(ident='http://example.com/context_1')
        self.assertEqual(len(ctx), 0)

    def test_len(self):
        ident_uri = 'http://example.com/context_1'
        ctx = Context(ident=ident_uri)
        for i in range(5):
            ctx.add_statement(create_mock_statement(ident_uri, i))
        self.assertEqual(len(ctx), 5)

    def test_add_remove_statement(self):
        ident_uri = 'http://example.com/context_1'
        ctx = Context(ident=ident_uri)
        stmt_to_remove = create_mock_statement(ident_uri, 42)
        for i in range(5):
            ctx.add_statement(create_mock_statement(ident_uri, i))
        ctx.add_statement(stmt_to_remove)
        ctx.remove_statement(stmt_to_remove)
        self.assertEqual(len(ctx), 5)

    def test_add_statement_with_different_context(self):
        ctx = Context(ident='http://example.com/context_1')
        stmt1 = create_mock_statement('http://example.com/context_2', 1)
        with self.assertRaises(ValueError):
            ctx.add_statement(stmt1)

    def test_contents_triples(self):
        res_wanted = []
        ident_uri = 'http://example.com/context_1'
        ctx = Context(ident=ident_uri)
        for i in range(5):
            stmt = create_mock_statement(ident_uri, i)
            ctx.add_statement(stmt)
            res_wanted.append(stmt.to_triple())
        for triples in ctx.contents_triples():
            self.assertTrue(triples in res_wanted)

    def test_clear(self):
        ident_uri = 'http://example.com/context_1'
        ctx = Context(ident=ident_uri)
        for i in range(5):
            ctx.add_statement(create_mock_statement(ident_uri, i))
        ctx.clear()
        self.assertEqual(len(ctx), 0)

    def test_save_context(self):
        graph = set()
        ident_uri = 'http://example.com/context_1'
        ctx = Context(ident=ident_uri)
        for i in range(5):
            ctx.add_statement(create_mock_statement(ident_uri, i))
        ctx.save_context(graph)
        self.assertEqual(len(graph), 5)

    def test_save_context_with_inline_imports(self):
        graph = set()
        ident_uri = 'http://example.com/context_1'
        ident_uri2 = 'http://example.com/context_2'
        ident_uri2_1 = 'http://example.com/context_2_1'
        ident_uri3 = 'http://example.com/context_3'
        ident_uri4 = 'http://example.com/context_4'
        ctx = Context(ident=ident_uri)
        ctx2 = Context(ident=ident_uri2)
        ctx2_1 = Context(ident=ident_uri2_1)
        ctx.add_import(ctx2)
        ctx.add_import(ctx2_1)
        ctx3 = Context(ident=ident_uri3)
        ctx3.add_import(ctx)
        last_ctx = Context(ident=ident_uri4)
        last_ctx.add_import(ctx3)
        ctx.add_statement(create_mock_statement(ident_uri, 1))
        ctx2.add_statement(create_mock_statement(ident_uri2, 2))
        ctx2_1.add_statement(create_mock_statement(ident_uri2_1, 2.1))
        ctx3.add_statement(create_mock_statement(ident_uri3, 3))
        last_ctx.add_statement(create_mock_statement(ident_uri4, 4))
        last_ctx.save_context(graph, True)
        self.assertEqual(len(graph), 5)

    def test_triples_saved(self):
        graph = set()
        ident_uri = 'http://example.com/context_1'
        ident_uri2 = 'http://example.com/context_2'
        ident_uri2_1 = 'http://example.com/context_2_1'
        ident_uri3 = 'http://example.com/context_3'
        ident_uri4 = 'http://example.com/context_4'
        ctx = Context(ident=ident_uri)
        ctx2 = Context(ident=ident_uri2)
        ctx2_1 = Context(ident=ident_uri2_1)
        ctx.add_import(ctx2)
        ctx.add_import(ctx2_1)
        ctx3 = Context(ident=ident_uri3)
        ctx3.add_import(ctx)
        last_ctx = Context(ident=ident_uri4)
        last_ctx.add_import(ctx3)
        ctx.add_statement(create_mock_statement(ident_uri, 1))
        ctx2.add_statement(create_mock_statement(ident_uri2, 2))
        ctx2_1.add_statement(create_mock_statement(ident_uri2_1, 2.1))
        ctx3.add_statement(create_mock_statement(ident_uri3, 3))
        last_ctx.add_statement(create_mock_statement(ident_uri4, 4))
        last_ctx.save_context(graph, True)
        self.assertEqual(last_ctx.triples_saved, 5)

    def test_triples_saved_noundef_triples_counted(self):
        graph = set()
        ident_uri = 'http://example.com/context_1'
        ctx = Context(ident=ident_uri)
        statement = MagicMock()
        statement.context.identifier = rdflib.term.URIRef(ident_uri)
        statement.to_triple.return_value = (Variable('var'), 1, 2)
        ctx.add_statement(statement)
        ctx.save_context(graph)
        self.assertEqual(ctx.triples_saved, 0)

    def test_triples_saved_multi(self):
        graph = set()
        ident_uri = 'http://example.com/context_1'
        ident_uri1 = 'http://example.com/context_11'
        ident_uri2 = 'http://example.com/context_12'
        ctx = Context(ident=ident_uri)
        ctx1 = Context(ident=ident_uri1)
        ctx2 = Context(ident=ident_uri2)
        ctx2.add_import(ctx)
        ctx1.add_import(ctx2)
        ctx1.add_import(ctx)

        ctx.add_statement(create_mock_statement(ident_uri, 1))
        ctx1.add_statement(create_mock_statement(ident_uri1, 3))
        ctx2.add_statement(create_mock_statement(ident_uri2, 2))
        ctx1.save_context(graph, inline_imports=True)
        self.assertEqual(ctx1.triples_saved, 3)

    def test_context_getter(self):
        ctx = Context(ident='http://example.com/context_1')
        self.assertIsNone(ctx.context)

    def test_context_setter(self):
        ctx = Context(ident='http://example.com/context_1')
        ctx.context = 42
        self.assertEqual(ctx.context, 42)


class ContextStoreTest(_DataTest):

    def test_query(self):
        rdf_type = 'http://example.org/A'
        ctxid = URIRef('http://example.com/context_1')
        ctx = Mock()
        graph = Mock()
        graph.store.triples.side_effect = ([], [((URIRef('anA0'), rdflib.RDF.type, rdf_type), (ctxid,))],)
        ctx.conf = {'rdf.graph': graph}

        ctx.contents_triples.return_value = [(URIRef('anA'), rdflib.RDF.type, rdf_type)]
        ctx.identifier = ctxid
        ctx.imports = []
        store = ContextStore(ctx, include_stored=True)
        self.assertEqual(set([URIRef('anA'), URIRef('anA0')]),
                         set(x[0][0] for x in store.triples((None, rdflib.RDF.type, rdf_type))))

    def test_contexts_staged_ignores_stored(self):
        ctxid0 = URIRef('http://example.com/context_0')
        ctxid1 = URIRef('http://example.com/context_1')
        ctx = Mock()
        graph = Mock()
        graph.store.triples.side_effect = [[((None, None, ctxid0), ())], []]
        ctx.conf = {'rdf.graph': graph}
        ctx.contents_triples.return_value = ()
        ctx.identifier = ctxid1
        ctx.imports = []
        store = ContextStore(ctx)
        self.assertNotIn(ctxid0, set(store.contexts()))

    def test_contexts_combined(self):
        ctxid0 = URIRef('http://example.com/context_0')
        ctxid1 = URIRef('http://example.com/context_1')
        ctx = Mock()
        graph = Mock()
        graph.store.triples.side_effect = [[((None, None, ctxid0), ())], []]
        ctx.conf = {'rdf.graph': graph}
        ctx.contents_triples.return_value = ()
        ctx.identifier = ctxid1
        ctx.imports = []
        store = ContextStore(ctx, include_stored=True)
        self.assertEqual(set([ctxid0, ctxid1]),
                         set(store.contexts()))

    def test_len_fail(self):
        ctx = Mock()
        graph = Mock()
        ctx.conf = {'rdf.graph': graph}
        ctx.contents_triples.return_value = ()
        ctx.imports = []
        store = ContextStore(ctx, include_stored=True)
        with self.assertRaises(NotImplementedError):
            len(store)


def create_mock_statement(ident_uri, stmt_id):
    statement = MagicMock()
    statement.context.identifier = rdflib.term.URIRef(ident_uri)
    statement.to_triple.return_value = (True, stmt_id, -stmt_id)
    return statement
