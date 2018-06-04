import rdflib
from rdflib.term import URIRef
from unittest.mock import MagicMock
from PyOpenWorm.dataObject import DataObject, InverseProperty
from PyOpenWorm.context import Context
from .DataTestTemplate import _DataTest


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
        expected = (URIRef('b'), URIRef(
            'http://openworm.org/entities/B/b'), URIRef('a'))
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

    def test_create_graph(self):
        ctx = Context(ident='http://example.com/context_1')
        graph = ctx.save_imports()
        self.assertEqual(len(graph), 0)

    def test_save_import(self):
        ctx = Context(ident='http://example.com/context_1')
        new_ctx = Context(ident='http://example.com/context_1')
        ctx.add_import(new_ctx)
        create_graph = ctx.save_imports()
        self.assertEqual(create_graph, ctx.save_imports())

    def test_add_import(self):
        ctx = Context(ident='http://example.com/context_1')
        ctx2 = Context(ident='http://example.com/context_2')
        ctx2_1 = Context(ident='http://example.com/context_2_1')
        ctx.add_import(ctx2)
        ctx.add_import(ctx2_1)
        ctx3 = Context(ident='http://example.com/context_3')
        ctx3.add_import(ctx)
        final_ctx = Context(
            ident='http://example.com/context_1', imported=(ctx3,))
        self.assertEqual(len(final_ctx.save_imports()), 4)

    def test_init_len(self):
        ctx = Context(ident='http://example.com/context_1')
        self.assertEqual(len(ctx), 0)

    def test_len(self):
        ident_uri = 'http://example.com/context_1'
        ctx = Context(ident=ident_uri)
        ctx.add_import(Context(ident=ident_uri))
        for i in range(0, 5):
            ctx.add_statement(create_mock_statement(ident_uri, i))
        self.assertEqual(len(ctx), 5)

    def test_add_remove_statement(self):
        ident_uri = 'http://example.com/context_1'
        ctx = Context(ident=ident_uri)
        stmt1 = create_mock_statement(ident_uri, 1)
        stmt2 = create_mock_statement(ident_uri, 2)
        stmt3 = create_mock_statement(ident_uri, 3)
        stmt4 = create_mock_statement(ident_uri, 4)
        [ctx.add_statement(stmt) for stmt in [stmt1, stmt2, stmt3, stmt4]]
        ctx.remove_statement(stmt2)
        self.assertTrue(len(list(ctx.contents_triples())), 3)

    def test_add_bad_statement(self):
        ctx = Context(ident='http://example.com/context_1')
        stmt1 = create_mock_statement('http://example.com/context_2', 1)
        with self.assertRaises(ValueError):
            ctx.add_statement(stmt1)

    def test_contents_triples(self):
        ident_uri = 'http://example.com/context_1'
        ctx = Context(ident=ident_uri)
        stmt1 = create_mock_statement(ident_uri, 1)
        stmt2 = create_mock_statement(ident_uri, 2)
        stmt3 = create_mock_statement(ident_uri, 3)
        stmt4 = create_mock_statement(ident_uri, 4)
        [ctx.add_statement(stmt) for stmt in [stmt1, stmt2, stmt3, stmt4]]
        self.assertTrue(all(ctx.contents_triples()))

    def test_clear(self):
        ident_uri = 'http://example.com/context_1'
        ctx = Context(ident=ident_uri)
        for i in range(5):
            ctx.add_statement(create_mock_statement(ident_uri, i))
        ctx.clear()
        self.assertEqual(len(list(ctx.contents_triples())), 0)

    def test_save_context(self):
        ident_uri = 'http://example.com/context_1'
        ctx = Context(ident=ident_uri)
        for i in range(5):
            ctx.add_statement(create_mock_statement(ident_uri, i))
        graph = ctx.save_context(set())
        self.assertEqual(ctx.tripcnt, 5)
        self.assertEqual(len(graph), 5)

    def test_save_context_with_inline_imports(self):
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
        graph = last_ctx.save_context(set(), True)
        self.assertEqual(len(graph), 5)

    def test_init_bool(self):
        ident_uri = 'http://example.com/context_1'
        ctx = Context(ident=ident_uri)
        self.assertFalse(ctx)

    def test_bool(self):
        ctx = Context(ident='http://example.com/context_1')
        ctx2 = Context(ident='http://example.com/context_2')
        ctx.add_import(ctx2)
        self.assertTrue(ctx)


def create_mock_statement(ident_uri, stmt_id):
    statement = MagicMock()
    statement.context.identifier = rdflib.term.URIRef(ident_uri)
    statement.to_triple.return_value = (True, stmt_id, -stmt_id)
    return statement
