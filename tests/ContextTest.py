from rdflib.term import URIRef
from rdflib.graph import ConjunctiveGraph
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
        final_ctx = Context(ident='http://example.com/context_1', imported=(ctx3,))
        self.assertEqual(len(final_ctx.save_imports()), 4)
